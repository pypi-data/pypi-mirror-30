import gspread
import typing


from .cache import cache
from .log import logger

__all__ = ["Worksheet", "VersionMatrixSheet", "VersionMatrixWorksheet"]


class Worksheet:
    @cache(key=lambda self, *args, **kwargs: (self.worksheet.id, args, kwargs))
    def get_row(self, row, min_col=2) -> typing.List[gspread.Cell]:
        return [cell for cell in self.worksheet.range(row, 1, row, self.worksheet.col_count) if cell.col >= min_col]

    @cache(key=lambda self, *args, **kwargs: (self.worksheet.id, args, kwargs))
    def get_column(self, col, min_row=2) -> typing.List[gspread.Cell]:
        return [cell for cell in self.worksheet.range(1, col, self.worksheet.row_count, col) if cell.row >= min_row]

    @staticmethod
    def __find_existing_cell(cells: typing.List[gspread.Cell], value: str) -> typing.Optional[gspread.Cell]:
        for cell in cells:
            if cell.value == value:
                return cell

    @staticmethod
    def __create_cell(cells: typing.List[gspread.Cell], value: str, updated_cells: typing.List[gspread.Cell]) -> typing.Optional[gspread.Cell]:
        for cell in cells:
            if cell.value in ("-", "_", "any"):
                cell.value = value
                updated_cells.append(cell)
                return cell

    def find_column_header(self, value: str) -> typing.Optional[gspread.Cell]:
        return self.__find_existing_cell(self.get_row(1), value)

    def find_or_create_column_header(self, value: str, updated_cells: typing.List[gspread.Cell]) -> typing.Optional[gspread.Cell]:
        cells = self.get_row(1)
        cell = self.__find_existing_cell(cells, value)
        if not cell:
            cell = self.__create_cell(cells, value, updated_cells)
        return cell

    def find_row_header(self, value: str) -> typing.Optional[gspread.Cell]:
        return self.__find_existing_cell(self.get_column(1), value)

    def find_or_create_row_header(self, value: str, updated_cells: typing.List[gspread.Cell]) -> typing.Optional[gspread.Cell]:
        cells = self.get_column(1)
        cell = self.__find_existing_cell(cells, value)
        if not cell:
            cell = self.__create_cell(cells, value, updated_cells)
        return cell


