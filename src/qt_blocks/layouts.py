from typing import Optional, Dict, List

from qtpy import QtCore, QtWidgets


class FlowLayout(QtWidgets.QLayout):
    """A layout that arranges widgets based on available horizontal space."""

    def __init__(self, parent: Optional[QtWidgets.QWidget] = None):
        super().__init__(parent)

        self._item_list = []

    # -- Reimplemented methods --------------------------------------------- #

    def addItem(self, item: QtWidgets.QLayoutItem):
        # this method is called under the hood by addWidget
        self._item_list.append(item)

    def insertWidget(self, index, widget):
        self.addChildWidget(widget)
        self._item_list.insert(index, QtWidgets.QWidgetItem(widget))
        self.invalidate()

    def count(self) -> int:
        return len(self._item_list)

    def itemAt(self, index: int) -> Optional[QtWidgets.QLayoutItem]:
        try:
            return self._item_list[index]
        except IndexError:
            return None

    def takeAt(self, index) -> QtWidgets.QLayoutItem:
        return self._item_list.pop(index)

    def hasHeightForWidth(self) -> bool:
        """Indicates that this widget supports QLayout.heightForWidth()."""
        return True

    def heightForWidth(self, width: int) -> int:
        """Calculates the expected total height of the widgets in the layout.

        Args:
            width (int): The width of the layout.
        """
        height = self._do_layout(QtCore.QRect(0, 0, width, 0), calculate_only=True)
        return height

    def setGeometry(self, rect: QtCore.QRect):
        super().setGeometry(rect)
        self._do_layout(rect, False)

    def sizeHint(self) -> QtCore.QSize:
        return self.minimumSize()

    def minimumSize(self) -> QtCore.QSize:
        size = QtCore.QSize()

        for item in self._item_list:
            size = size.expandedTo(item.minimumSize())

        size += QtCore.QSize(
            self.contentsMargins().top() * 2, self.contentsMargins().top() * 2
        )
        return size

    def expandingDirections(self) -> QtCore.Qt.Orientations:
        return QtCore.Qt.Horizontal

    # -- Layout Management ------------------------------------------------- #

    def _do_layout(self, rect: QtCore.QRect, calculate_only: bool) -> int:
        """Performs the actual layout calculation.

        Args:
            rect (QtCore.QRect): The rectangle to lay the widgets out in. This
                is not the entire area of the layout, but we need an upper-left
                corner to start from.
            calculate_only (bool): If True, the layout will not be applied to
                the widgets, but the height of the layout will be calculated.

        Returns:
            int: The total height of the layout with all widgets placed.
        """
        x = rect.x()
        y = rect.y()
        line_height = 0
        spacing = self.spacing()

        for item in self._item_list:
            next_x = x + item.sizeHint().width() + spacing
            if next_x - spacing > rect.right() and line_height > 0:
                x = rect.x()
                y = y + line_height + spacing
                next_x = x + item.sizeHint().width() + spacing
                line_height = 0

            if not calculate_only:
                item.setGeometry(QtCore.QRect(QtCore.QPoint(x, y), item.sizeHint()))

            x = next_x
            line_height = max(line_height, item.sizeHint().height())

        return y + line_height - rect.y()


class ColumnManager:
    """Helper class for managing widgets organized into columns.

    This class is intended to be used with the ColumnLayout class, where the
    ColumnManager instance will unify the widths of widgets in multiple
    layouts.

    See the ColumnLayout class for more information.
    """

    default_spacing = 5

    def __init__(self, spacing: Optional[int] = None):
        """
        Args:
            spacing (int, optional): The spacing between columns, in pixels.
        """
        self._spacing = spacing or self.default_spacing

        # The width of each column, in pixels.
        self.column_widths: Dict[int, int] = dict()

        # The layouts that are managed by this instance.  ColumnLayout classes
        # must register themselves with a ColumnManager instance
        self.managed_layouts: List[ColumnLayout] = list()

        # The columns that should be stretched to fill available space.
        self.stretch_columns: List[int] = []

        # The cached widths of each column, in pixels.
        self.cached_widths: Dict[int, int] = dict()

    @property
    def spacing(self) -> int:
        return self._spacing

    @spacing.setter
    def spacing(self, value: int):
        self._spacing = value
        self.invalidate()

    def set_column_width(self, column: int, width: int):
        """Set a fixed width for a column"""
        self.column_widths[column] = width
        self.invalidate()

    def invalidate(self):
        """Invalidate the cached widths of all columns."""
        self.cached_widths.clear()

    @property
    def column_count(self) -> int:
        """The number of columns in the managed layouts.

        Raises:
            ValueError: If the layouts have different column counts, the
                column count cannot be determined.
        """
        counts = list(set(layout.count() for layout in self.managed_layouts))
        if len(counts) > 1:
            raise ValueError("Column layouts have different column counts.")
        return counts[0]

    def get_nominal_column_width(self, column: int) -> int:
        """Get the width of a column without any stretch.

        Typically, this will be the minimum size hint of the largest widget in
        the column.
        """
        managed_widgets = [layout.itemAt(column) for layout in self.managed_layouts]
        width = max([widget.sizeHint().width() for widget in managed_widgets if widget])
        return width

    def get_column_width(self, column: int, rect: QtCore.QRect) -> int:
        """Get the actual column width for a column.

        This includes stretched and fixed widths.
        """
        # no geometry changes have happened, just return the width
        if column in self.cached_widths:
            width = self.cached_widths[column]

        # fixed width
        elif column in self.column_widths:
            width = self.column_widths[column]

        # column is allowed to stretch
        elif column in self.stretch_columns:
            width = self.get_stretchable_width(column, rect) // len(
                self.stretch_columns
            )
            return self.get_nominal_column_width(column) + width

        # use the nominal width
        else:
            width = self.get_nominal_column_width(column)

        self.cached_widths[column] = width

        return width

    def get_column_position(self, column: int, rect: QtCore.QRect) -> int:
        """Get the x position of a column."""
        column += 1
        x = rect.x()
        for i in range(column):
            x += self.get_column_width(i, rect) + self.spacing
        return x - self.spacing

    def get_summed_nominal_width(self):
        """Get the total width of all columns and spacing without any stretch."""
        width = sum(
            self.get_nominal_column_width(column_number)
            for column_number in range(self.column_count)
        )
        width += self.spacing * (self.column_count)
        return width

    def get_stretchable_width(self, column: int, rect: QtCore.QRect) -> int:
        """Get the remaining area of the layout that can be stretched."""
        total = rect.width() - self.get_summed_nominal_width()
        return max(0, total)

    def register(self, layout: "ColumnLayout"):
        """Add a layout to this manager."""
        self.managed_layouts.append(layout)


class ColumnLayout(QtWidgets.QHBoxLayout):
    """A layout that arranges widgets into aligned columns.

    This layout is intended to be used with the ColumnManager class, which will
    unify the widths of widgets in multiple layouts.

    It's up to the user to ensure that row widgets using ColumnLayouts are
    lined up in order to take advantage of this feature.

    Example::

        manager = ColumnManager()
        row_one = QtWidgets.QFrame()
        row_one.setLayout(ColumnLayout(manager))
        row_two = QtWidgets.QFrame()
        row_two.setLayout(ColumnLayout(manager))

        row_one.layout().addWidget(QtWidgets.QLabel("spam"))
        row_one.layout().addWidget(QtWidgets.QPushButton("eggs")
        row_two.layout().addWidget(QtWidgets.QLabel("baked beans"))
        row_two.layout().addWidget(QtWidgets.QPushButton("and spam")

    This example lays out the widgets like this::

            spam        | [eggs    ]
            baked beans | [and spam]

    Each column's width is based on the minimum width hint of the largest item
    in that column.

    The width of the columns can be set explicitly using the `column_widths`
    dictionary on the ColumnManager instance.

    The width of the columns can also be set to fill available space by adding
    the column number to the `stretch_columns` list on the ColumnManager.

    The same effect can be achieved with GridLayouts, but they require you to
    treat each cell of the grid as a separate widget, making hierarchical
    and modular design more difficult.  Additionally, each row in a grid layout
    must be contiguous, making aligning of discontinuous widgets impossible.
    """

    def __init__(
        self, manager: ColumnManager, parent: Optional[QtWidgets.QWidget] = None
    ):
        super().__init__(parent)
        self.manager = manager
        self.manager.register(self)
        self.item_list = []
        self._rect = QtCore.QRect()

    # -- Reimplemented methods --------------------------------------------- #

    def invalidate(self):
        super().invalidate()
        self._rect = None

    def setSpacing(self, spacing: int):
        raise NotImplementedError("Spacing is managed by the ColumnManager.")

    def spacing(self) -> int:
        return self.manager.spacing

    def setGeometry(self, rect: QtCore.QRect):
        super().setGeometry(rect)
        self._do_layout(rect)

    def sizeHint(self) -> QtCore.QSize:
        return self.minimumSize()

    def minimumSize(self) -> QtCore.QSize:
        size = QtCore.QSize()

        max_height = max(
            self.itemAt(i).minimumSize().height() for i in range(self.count())
        )
        width = self.manager.get_summed_nominal_width()

        # take spacing into account
        size.setHeight(max_height)
        size.setWidth(width)
        return size

    def _do_layout(self, rect: QtCore.QRect):
        """Performs the actual layout calculation.

        Args:
            rect (QtCore.QRect): The rectangle to lay the widgets out in. This
                should be provided by the parent widget's geometry.
        """
        if rect == self._rect:
            return
        self._rect = rect
        rect = self.alignmentRect(rect)
        self.manager.invalidate()
        x = rect.x()
        y = rect.y()
        spacing = self.spacing()
        for i in range(self.count()):
            item = self.itemAt(i)
            row_height = rect.height()
            column_width = self.manager.get_column_width(i, rect)
            new_geo = QtCore.QRect(x, y, column_width, row_height)
            item.setGeometry(new_geo)
            x += column_width + spacing
