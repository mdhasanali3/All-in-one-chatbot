"""Document processing utilities for RAG."""
import os
from typing import List, Dict
from pathlib import Path
import pypdf
from docx import Document
import pandas as pd

from backend.shared import setup_logger

logger = setup_logger(__name__)


class DocumentProcessor:
    """Process different document types for RAG ingestion."""

    @staticmethod
    def extract_text_from_pdf(file_path: str) -> str:
        """
        Extract text from PDF file.

        Args:
            file_path: Path to PDF file

        Returns:
            Extracted text
        """
        try:
            text = ""
            with open(file_path, 'rb') as file:
                pdf_reader = pypdf.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
            logger.info(f"Extracted text from PDF: {file_path}")
            return text
        except Exception as e:
            logger.error(f"Failed to extract PDF text: {str(e)}")
            raise

    @staticmethod
    def extract_text_from_docx(file_path: str) -> str:
        """
        Extract text from DOCX file.

        Args:
            file_path: Path to DOCX file

        Returns:
            Extracted text
        """
        try:
            doc = Document(file_path)
            text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
            logger.info(f"Extracted text from DOCX: {file_path}")
            return text
        except Exception as e:
            logger.error(f"Failed to extract DOCX text: {str(e)}")
            raise

    @staticmethod
    def extract_text_from_excel(file_path: str) -> str:
        """
        Extract text from Excel file.

        Args:
            file_path: Path to Excel file

        Returns:
            Extracted text
        """
        try:
            df = pd.read_excel(file_path, sheet_name=None)
            text = ""
            for sheet_name, sheet_df in df.items():
                text += f"\n--- Sheet: {sheet_name} ---\n"
                text += sheet_df.to_string(index=False) + "\n"
            logger.info(f"Extracted text from Excel: {file_path}")
            return text
        except Exception as e:
            logger.error(f"Failed to extract Excel text: {str(e)}")
            raise

    @staticmethod
    def extract_text_from_csv(file_path: str) -> str:
        """
        Extract text from CSV file.

        Args:
            file_path: Path to CSV file

        Returns:
            Extracted text
        """
        try:
            df = pd.read_csv(file_path)
            text = df.to_string(index=False)
            logger.info(f"Extracted text from CSV: {file_path}")
            return text
        except Exception as e:
            logger.error(f"Failed to extract CSV text: {str(e)}")
            raise

    @staticmethod
    def extract_text_from_txt(file_path: str) -> str:
        """
        Extract text from TXT file.

        Args:
            file_path: Path to TXT file

        Returns:
            Extracted text
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                text = file.read()
            logger.info(f"Extracted text from TXT: {file_path}")
            return text
        except Exception as e:
            logger.error(f"Failed to extract TXT text: {str(e)}")
            raise

    def process_document(self, file_path: str) -> Dict[str, str]:
        """
        Process document based on file type.

        Args:
            file_path: Path to document

        Returns:
            Dictionary with filename and extracted text
        """
        file_extension = Path(file_path).suffix.lower()

        extractors = {
            '.pdf': self.extract_text_from_pdf,
            '.docx': self.extract_text_from_docx,
            '.xlsx': self.extract_text_from_excel,
            '.xls': self.extract_text_from_excel,
            '.csv': self.extract_text_from_csv,
            '.txt': self.extract_text_from_txt
        }

        if file_extension not in extractors:
            raise ValueError(f"Unsupported file type: {file_extension}")

        text = extractors[file_extension](file_path)

        return {
            "filename": os.path.basename(file_path),
            "text": text,
            "file_type": file_extension
        }

    def chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """
        Split text into overlapping chunks.

        Args:
            text: Text to chunk
            chunk_size: Size of each chunk in characters
            overlap: Overlap between chunks

        Returns:
            List of text chunks
        """
        chunks = []
        start = 0
        text_length = len(text)

        while start < text_length:
            end = start + chunk_size
            chunk = text[start:end]
            chunks.append(chunk)
            start += chunk_size - overlap

        logger.info(f"Created {len(chunks)} chunks from text")
        return chunks
