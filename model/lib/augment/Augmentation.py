import asyncio
import csv
import logging
import os
import aiofiles
import enums
from data import ELEMENT_PATHS

from lib.augment.AugmentType import AugmentationType
from lib.util.list_extensions import group_by, chunked
from lib.util.openai.GPTClient import GPTClient

MAX_PER_REQUEST = 25


class Augmentation:
    def __init__(self, augmentation_type: AugmentationType):

        self.logger = logging.getLogger("Athena | Augmentation")

        self.augmentation_type = augmentation_type
        self.gpt_client: GPTClient | None = None
        self.input_path = augmentation_type.input_directory()
        self.output_path = augmentation_type.output_directory()

        self.lock = asyncio.locks.Lock()

    def start(self):
        asyncio.run(self._run())

    async def _run(self):
        self.logger.info("Creating client")
        await self.create_gpt_client()

        for element, name in ELEMENT_PATHS.items():
            csv_name = name + ".csv"
            input_path = self.input_path + csv_name
            output_path = self.output_path + csv_name

            self.logger.debug(f"Processing element type: {name} with input path: {input_path}")
            data = await self.read_csv(input_path)
            if not data:
                self.logger.error("No data found in CSV.")
                continue

            grouped_data: dict[int, list[tuple[str, str]]] = group_by(data, lambda x: x[0])

            for ordinal, data in grouped_data.items():
                self.logger.info(f"Processing: Aug Type: {self.augmentation_type.name} | Element: {name} | Type: {ordinal} | Size: {len(data):,} all results in {name} with ordinal {ordinal}: Size: {len(data)}")
                sentences = list(set([row[1].replace('"', '').lstrip() for row in data]))
                self.logger.debug(f"Sentences created!")

                # Process augmentation in chunks.
                chunks = list(chunked(sentences, MAX_PER_REQUEST))
                tasks = [asyncio.create_task(self.gpt_client.process_batch(chunk)) for chunk in chunks]
                self.logger.debug("Tasks created!")

                augmented_results: list[dict[str, list[str]]] = []
                for i, task in enumerate(asyncio.as_completed(tasks)):
                    try:
                        result: dict[str, list[str]] | None = await task
                        self.logger.debug(f"Result retrieved for task {i}")
                        if not result:
                            self.logger.error(f"hunk {i} failed!")
                        else:
                            augmented_results.append(result)
                    except Exception as e:
                        self.logger.error(f"Chunk {i} failed with error: {e}")

                self.logger.info("Processing complete!")
                csv_rows: list[tuple[int, str]] = []

                for result in list(augmented_results):
                    for key, value in result.items():
                        csv_rows.append((ordinal, key))
                        csv_rows.extend([(ordinal, sentence) for sentence in value])

                csv_string = "\n".join([f'{row[0]},"{row[1]}"' for row in csv_rows]) + "\n"


                os.makedirs(self.output_path, exist_ok=True)
                async with self.lock:
                    async with aiofiles.open(output_path, mode='a+', encoding='utf-8') as f:
                        await f.seek(0)
                        # Check if the file is empty before writing the header
                        file_content = await f.read()
                        if not file_content.strip():  # If the file is empty, write the header
                            await f.write("type,sentence\n")
                        await f.write(csv_string)

            self.logger.info(f"Processing complete for {name}")

    async def read_csv(self, file_path: str):
        # If file_path is empty, use a default CSV file.
        rows = []
        with open(file_path, mode='r+', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader, None)  # skip header, if any
            for row in reader:
                if len(row) >= 2:
                    # Keep both the ordinal (row[0]) and the sentence (row[1])
                    rows.append((row[0], row[1]))
        return rows

    async def create_gpt_client(self):
        prompt = self.augmentation_type.get_prompt()
        self.gpt_client = await GPTClient.create(
            name=f"Athena-{self.augmentation_type.name}",
            model="gpt-4o-mini",
            system_prompt=prompt
        )


def main():
    for aug_type in AugmentationType:
        augmentation = Augmentation(aug_type)
        augmentation.logger.info(f"\n\nStarting Augmentation for {aug_type.name}\n\n")
        augmentation.start()
        augmentation.logger.info(f"\n\nAugmentation complete for {aug_type.name}!\n\n")
