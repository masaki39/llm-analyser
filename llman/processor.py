"""CSV processing with LLM-powered data generation."""

import json
import logging
from pathlib import Path
from typing import List, Optional, Type

import pandas as pd
from pydantic import BaseModel

from .llm_client import LLMClient
from .schemas import get_field_names
from .utils import format_error_message

logger = logging.getLogger(__name__)


class CSVProcessor:
    """Process CSV files with LLM to generate new structured columns."""

    def __init__(self, llm_client: LLMClient):
        """Initialize the CSV processor.

        Args:
            llm_client: An initialized LLM client instance.
        """
        self.llm_client = llm_client

    def _should_process_row(self, row: pd.Series, new_column_names: List[str]) -> bool:
        """Check if a row should be processed (has empty values in new columns).

        Args:
            row: DataFrame row
            new_column_names: List of new column names to check

        Returns:
            True if row should be processed, False if already filled
        """
        for col in new_column_names:
            if col in row.index:
                value = row[col]
                # Check if value is missing or empty
                if pd.isna(value) or value == "":
                    return True
                # Try to parse as JSON and check if empty
                try:
                    parsed = json.loads(str(value))
                    if not parsed or parsed == {}:
                        return True
                except (json.JSONDecodeError, TypeError, ValueError):
                    # Not valid JSON, keep existing value
                    pass
        # If none of the columns exist, we should process
        if not any(col in row.index for col in new_column_names):
            return True
        # All columns have data
        return False

    def process_csv(
        self,
        input_path: Path | str,
        output_path: Path | str,
        columns: List[str],
        prompt: str,
        response_model: Optional[Type[BaseModel]] = None,
        resume: bool = True,
    ) -> None:
        """Process a CSV file and add LLM-generated columns.

        Args:
            input_path: Path to the input CSV file.
            output_path: Path to the output CSV file.
            columns: List of column names to use as input for LLM.
            prompt: User-provided prompt describing the task.
            response_model: Optional Pydantic model for structured output.
            resume: If True and output exists, skip rows with data.

        Raises:
            FileNotFoundError: If input file doesn't exist.
            ValueError: If specified columns don't exist in CSV.
        """
        input_path = Path(input_path)
        output_path = Path(output_path)

        if not input_path.exists():
            raise FileNotFoundError(f"Input file not found: {input_path}")

        # Load CSV - use output if it exists and resume is True
        if output_path.exists() and resume:
            logger.info(f"Resuming: Loading existing output from {output_path}...")
            df = pd.read_csv(output_path)
            logger.info(f"Loaded {len(df)} rows (resume mode)")
        else:
            logger.info(f"Loading CSV from {input_path}...")
            df = pd.read_csv(input_path)
            logger.info(f"Loaded {len(df)} rows")

        # Validate columns
        missing_cols = set(columns) - set(df.columns)
        if missing_cols:
            raise ValueError(
                f"Columns not found in CSV: {missing_cols}\n"
                f"Available columns: {list(df.columns)}"
            )

        # Determine new column names
        if response_model is not None:
            new_column_names = get_field_names(response_model)
        else:
            # Will be determined dynamically from first result
            new_column_names = []

        # Process each row
        logger.info(
            f"\nProcessing rows with LLM (model: {self.llm_client.model_name})..."
        )
        logger.info(f"Using columns: {columns}")
        logger.info(f"Prompt: {prompt}")
        if response_model:
            logger.info(f"Schema: {get_field_names(response_model)}")
        logger.info("")

        results = []
        failed_rows = []
        processed = 0
        skipped = 0

        for idx, row in df.iterrows():
            row_num = idx + 1
            result_position = len(results)

            # Check if row should be skipped (resume mode)
            if (
                resume
                and new_column_names
                and not self._should_process_row(row, new_column_names)
            ):
                logger.info(f"Row {row_num}/{len(df)}: ✓ Skipping (already processed)")
                # Keep existing data
                existing_data = {
                    col: row[col] if col in row.index else None
                    for col in new_column_names
                }
                results.append(existing_data if existing_data else {})
                skipped += 1
                continue

            logger.info(f"Processing row {row_num}/{len(df)}...")

            try:
                # Extract input data from selected columns
                input_data = {col: row[col] for col in columns}

                # Generate structured output
                output = self.llm_client.generate_structured_output(
                    prompt, input_data, response_model
                )

                results.append(output)
                processed += 1
                logger.info(f"Row {row_num}/{len(df)}: ✓ Success")

            except Exception as e:
                logger.error(
                    f"Row {row_num}/{len(df)}: ✗ Error: {format_error_message(e)}"
                )
                # Add empty result to maintain row alignment
                results.append({})
                processed += 1
                failed_rows.append(
                    {
                        "position": result_position,
                        "row": row.copy(),
                        "row_num": row_num,
                        "error": format_error_message(e),
                    }
                )

        # Attempt fallback retries for failed rows before finalizing results
        if failed_rows:
            failed_rows = self._retry_failed_rows(
                failed_rows, results, columns, prompt, response_model
            )

        errors = [f"Row {info['row_num']}: {info['error']}" for info in failed_rows]

        # Convert results to DataFrame columns
        if results:
            # Flatten nested JSON into columns
            result_df = pd.json_normalize(results)
            result_df = result_df.reindex(df.index)

            # Overwrite existing columns (or create new ones) with LLM output
            for col in result_df.columns:
                df[col] = result_df[col]

        output_df = df

        # Save output
        logger.info(f"\nSaving results to {output_path}...")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_df.to_csv(output_path, index=False)
        logger.info(f"✓ Saved {len(output_df)} rows")

        # Print summary
        logger.info(f"\n{'='*60}")
        logger.info("Processing Summary:")
        logger.info(f"  Total rows: {len(df)}")
        logger.info(f"  Processed: {processed}")
        logger.info(f"  Skipped: {skipped}")
        logger.info(f"  Successful: {processed - len(errors)}")
        logger.info(f"  Errors: {len(errors)}")

        if errors:
            logger.warning("\nErrors encountered:")
            for error in errors[:10]:  # Show first 10 errors
                logger.warning(f"  - {error}")
            if len(errors) > 10:
                logger.warning(f"  ... and {len(errors) - 10} more errors")

        logger.info(f"{'='*60}")

    def _retry_failed_rows(
        self,
        failed_rows,
        results: List[dict],
        columns: List[str],
        prompt: str,
        response_model: Optional[Type[BaseModel]] = None,
    ):
        """Retry rows that failed during the initial pass.

        Args:
            failed_rows: List of failure metadata dicts.
            results: List of per-row outputs to update.
            columns: Columns to read from the input row.
            prompt: Prompt to send to the LLM.
            response_model: Optional response schema.

        Returns:
            List of failure metadata that still failed after retry.
        """
        logger.info(
            f"\nRetrying {len(failed_rows)} failed row(s) to avoid empty outputs..."
        )
        remaining_failures = []

        for failure in failed_rows:
            row = failure["row"]
            row_num = failure["row_num"]
            position = failure["position"]

            try:
                input_data = {col: row[col] for col in columns}
                output = self.llm_client.generate_structured_output(
                    prompt, input_data, response_model
                )
                results[position] = output
                logger.info(f"Row {row_num}: ✓ Success on fallback retry")
            except Exception as retry_error:
                formatted = format_error_message(retry_error)
                failure["error"] = formatted
                remaining_failures.append(failure)
                logger.error(f"Row {row_num}: ✗ Fallback retry failed: {formatted}")

        if remaining_failures:
            logger.warning(
                f"\nUnable to recover {len(remaining_failures)} row(s) after fallback."
            )
        else:
            logger.info("All failed rows recovered successfully.")

        return remaining_failures

    def preview_sample(
        self,
        input_path: Path | str,
        columns: List[str],
        prompt: str,
        num_rows: int = 3,
        response_model: Optional[Type[BaseModel]] = None,
    ) -> None:
        """Preview LLM output on a sample of rows without saving.

        Args:
            input_path: Path to the input CSV file.
            columns: List of column names to use as input for LLM.
            prompt: User-provided prompt describing the task.
            num_rows: Number of rows to preview (default: 3).
            response_model: Optional Pydantic model for structured output.
        """
        input_path = Path(input_path)

        if not input_path.exists():
            raise FileNotFoundError(f"Input file not found: {input_path}")

        # Load CSV
        df = pd.read_csv(input_path)

        # Validate columns
        missing_cols = set(columns) - set(df.columns)
        if missing_cols:
            raise ValueError(
                f"Columns not found in CSV: {missing_cols}\n"
                f"Available columns: {list(df.columns)}"
            )

        # Process sample rows
        logger.info(f"Preview: Processing {num_rows} sample rows...\n")
        sample_df = df.head(num_rows)

        for idx, row in sample_df.iterrows():
            row_num = idx + 1
            logger.info(f"{'='*60}")
            logger.info(f"Row {row_num}:")
            logger.info(f"{'='*60}")

            # Show input data
            logger.info("Input:")
            for col in columns:
                value = row[col]
                # Truncate long values
                if isinstance(value, str) and len(value) > 100:
                    value = value[:100] + "..."
                logger.info(f"  {col}: {value}")

            try:
                # Extract input data
                input_data = {col: row[col] for col in columns}

                # Generate output
                output = self.llm_client.generate_structured_output(
                    prompt, input_data, response_model
                )

                # Show output
                logger.info("\nOutput:")
                logger.info(json.dumps(output, ensure_ascii=False, indent=2))

            except Exception as e:
                logger.error(f"\n✗ Error: {format_error_message(e)}")

            logger.info("")
