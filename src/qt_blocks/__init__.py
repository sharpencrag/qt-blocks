import typing as t

from qtpy import QtWidgets, QtCore

from qt_blocks import layouts

# aliases for convenience
_size_policy = QtWidgets.QSizePolicy
Qt = QtCore.Qt


class Block(QtWidgets.QFrame):
    """Base class for all blocks.

    The Block class should not be instantiated directly.  Instead, use one of
    the subclasses, or create a new subclass.
    """

    def __init__(
        self,
        layout_type: t.Type[QtWidgets.QLayout],
        margins: t.Optional[t.Union[t.Sequence[int], int]] = None,
        spacing: t.Optional[int] = None,
        parent: t.Optional[QtCore.QObject] = None,
        args=[],
        kwargs=dict(),
    ):
        """
        Args:
            layout_type (type): The QLayout to use for this block.  Must be a
                class, not an instance.
            margins (int, sequence, optional): The initial margins to set. If a
                single value is provided, it will be applied to all sides. If
                None, no margins will be set.
            spacing (int, optional): The spacing to set on the layout. If None,
                no spacing will be set.  Only affects layouts that support
                spacing.
            parent: The parent widget.
        """
        super().__init__(parent=parent)
        self._layout = layout_type(*args, **kwargs)
        self._set_initial_layout_params(margins, spacing)
        self.setLayout(self._layout)
        self._widgets = list()

    def _set_initial_layout_params(
        self,
        margins: t.Optional[t.Union[t.Sequence[int], int]],
        spacing: t.Optional[int],
    ):
        if margins is not None:
            self.set_margins(self._layout, margins)
        if spacing is not None:
            self._layout.setSpacing(spacing)

    @property
    def layout(self):
        """Interface to the main layout of this block.

        Block subclasses that have child widgets or nested layouts should
        re-implement this property.
        """
        return self._layout

    def _set_margin(self, index, value):
        """Set a single margin value."""
        margins = list(self.margins)
        margins[index] = value
        self.margins = margins

    # -- Interface Methods and Properties ---------------------------------- #
    # these methods provide a convenient way to access functionality on child
    # widgets and layouts.

    def add(self, widget: QtWidgets.QWidget):
        """Add a widget to the block layout."""
        if widget is None:
            return
        self.layout.addWidget(widget)
        self._widgets.append(widget)

    def insert(self, index, widget):
        """Insert a widget into the block layout at the given index.

        Note that this only works if the layout supports insertions at a single
        index, such as QBoxLayouts.
        """
        layout = t.cast(QtWidgets.QBoxLayout, self.layout)
        layout.insertWidget(index, widget)
        self._widgets.insert(index, widget)

    @property
    def margins(self):
        margins_obj = self.layout.contentsMargins()
        return [
            margins_obj.left(),
            margins_obj.top(),
            margins_obj.right(),
            margins_obj.bottom(),
        ]

    @margins.setter
    def margins(self, margins: t.Union[t.Sequence[int], int]):
        self.set_margins(self.layout, margins)

    def set_margins(self, layout, margins: t.Union[t.Sequence[int], int]):
        if isinstance(margins, int):
            margins = [margins] * 4
        layout.setContentsMargins(*margins)

    @property
    def margin_left(self):
        return self.margins[0]

    @margin_left.setter
    def margin_left(self, margin: int):
        self._set_margin(0, margin)

    @property
    def margin_top(self):
        return self.margins[1]

    @margin_top.setter
    def margin_top(self, margin: int):
        self._set_margin(1, margin)

    @property
    def margin_right(self):
        return self.margins[2]

    @margin_right.setter
    def margin_right(self, margin: int):
        self._set_margin(2, margin)

    @property
    def margin_bottom(self):
        return self.margins[3]

    @margin_bottom.setter
    def margin_bottom(self, margin: int):
        self._set_margin(3, margin)

    @property
    def spacing(self):
        return self.layout.spacing()

    @spacing.setter
    def spacing(self, spacing: int):
        self.layout.setSpacing(spacing)

    def align_left(self):
        self.layout.setAlignment(Qt.AlignLeft)

    def align_right(self):
        self.layout.setAlignment(Qt.AlignRight)

    def align_bottom(self):
        self.layout.setAlignment(Qt.AlignBottom)

    def align_top(self):
        self.layout.setAlignment(Qt.AlignTop)

    @property
    def widget(self):
        if len(self.widgets) == 1:
            return self.widgets[0]
        else:
            raise ValueError(
                "Block has multiple widgets.  Use `block.widgets` instead."
            )

    @widget.setter
    def widget(self, widget):
        self.widgets = (widget,)

    @property
    def widgets(self):
        return self._widgets

    @widgets.setter
    def widgets(self, new_widgets):
        """Declarative way to set the widgets in the block layout.

        This will remove any existing widgets from the layout.
        """
        for existing_widget in self.widgets:
            self.layout.takeAt(self.layout.indexOf(existing_widget))
            if existing_widget not in new_widgets:
                existing_widget.setParent(None)
                existing_widget.deleteLater()
        self._widgets = list()
        for widget in new_widgets:
            self.add(widget)

    def set_widgets(self, widgets):
        """Alias for widgets property setter."""
        self.widgets = widgets

    def set_shrinkwraps(self):
        self.setSizePolicy(_size_policy.Minimum, _size_policy.Minimum)

    def set_shrinkwraps_horizontal(self):
        self.setSizePolicy(_size_policy.Minimum, self.sizePolicy().verticalPolicy())

    def set_shrinkwraps_vertical(self):
        self.setSizePolicy(self.sizePolicy().horizontalPolicy(), _size_policy.Minimum)

    def set_uses_preferred_size(self):
        self.setSizePolicy(_size_policy.Preferred, _size_policy.Preferred)

    def set_uses_preferred_size_horizontal(self):
        self.setSizePolicy(_size_policy.Preferred, self.sizePolicy().verticalPolicy())

    def set_uses_preferred_size_vertical(self):
        self.setSizePolicy(self.sizePolicy().horizontalPolicy(), _size_policy.Preferred)

    # NOTE: MinimumExpanding is used in place of Expanding because it enforces the
    #       minimum size hint.  This can help prevent widgets from collapsing on top
    #       of each other in some cases.

    def set_expands(self):
        self.setSizePolicy(_size_policy.MinimumExpanding, _size_policy.MinimumExpanding)

    def set_expands_horizontal(self):
        self.setSizePolicy(
            _size_policy.MinimumExpanding, self.sizePolicy().verticalPolicy()
        )

    def set_expands_vertical(self):
        self.setSizePolicy(
            self.sizePolicy().horizontalPolicy(), _size_policy.MinimumExpanding
        )


class VBlock(Block):
    """A Block with a vertical layout."""

    def __init__(self, margins=None, spacing=None, parent=None):
        super().__init__(
            QtWidgets.QVBoxLayout, margins=margins, spacing=spacing, parent=parent
        )


class HBlock(Block):
    """A Block with a horizontal layout."""

    def __init__(self, margins=None, spacing=None, parent=None):
        super().__init__(
            QtWidgets.QHBoxLayout, margins=margins, spacing=spacing, parent=parent
        )


class FlowBlock(Block):
    """A Block with a flow layout."""

    def __init__(self, margins=None, spacing=None, parent=None):
        super().__init__(
            layouts.FlowLayout, margins=margins, spacing=spacing, parent=parent
        )


class ColumnsBlock(Block):
    """A Block with a layout of aligned columns.

    This class requires you to provide a ColumnManager instance for alignment.
    """

    def __init__(self, manager: layouts.ColumnManager, parent=None):
        args = (manager,)
        super().__init__(layouts.ColumnLayout, parent=parent, args=args)


class GridBlock(Block):
    """A Block with a grid layout."""

    def __init__(self, parent=None):
        super().__init__(QtWidgets.QGridLayout, parent)
        self._layout: QtWidgets.QGridLayout

    def add(self, widget, row, column, row_span=1, column_span=1):
        self.widgets.append(widget)
        self.layout.addWidget(widget, row, column, row_span, column_span)

    @property
    def rows(self):
        return self.layout.rowCount()

    @property
    def columns(self):
        return self.layout.columnCount()

    @property
    def column_spacing(self):
        return self.layout.horizontalSpacing()

    @column_spacing.setter
    def column_spacing(self, spacing: int):
        self.layout.setHorizontalSpacing(spacing)

    @property
    def row_spacing(self):
        return self.layout.verticalSpacing()

    @row_spacing.setter
    def row_spacing(self, spacing: int):
        self.layout.setVerticalSpacing(spacing)


class ScrollBlock(Block):
    """A Block with an embedded scroll area.

    This class should not be instantiated directly.  Instead, use one of the
    ScrollBlock subclasses or create a new subclass.
    """

    def __init__(self, inner_block_type, parent=None):
        super().__init__(QtWidgets.QVBoxLayout, margins=0, spacing=0, parent=parent)
        self.scroll_area = QtWidgets.QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.inner_block = inner_block_type()
        self.scroll_area.setWidget(self.inner_block)
        self._layout.addWidget(self.scroll_area)

    @property
    def layout(self):
        return self.inner_block.layout

    def always_show_scrollbar(self):
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)


class VScrollBlock(ScrollBlock):
    """A Block with a vertical scroll area."""

    def __init__(self, parent=None):
        super().__init__(VBlock, parent)

    def always_show_scrollbar(self):
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)


class HScrollBlock(ScrollBlock):
    """A Block with a horizontal scroll area."""

    def __init__(self, parent=None):
        super().__init__(HBlock, parent)

    def always_show_scrollbar(self):
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)


class FlowScrollBlock(ScrollBlock):
    """A Block with a flow scroll area."""

    def __init__(self, parent=None):
        super().__init__(FlowBlock, parent)


class GroupBlock(Block):
    """A Block with an embedded group box.

    This class should not be instantiated directly.  Instead, use one of the
    GroupBlock subclasses or create a new subclass.

    By default, the group box and its embedded block will have margins. To
    remove margins from outside group box, call `block.zero_outer_margins()`.
    """

    def __init__(
        self, inner_block_type: t.Type[Block], title: t.Optional[str], parent=None
    ):
        """
        Args:
            inner_block_type: The type of block to embed in the group box."""
        super().__init__(QtWidgets.QVBoxLayout, parent)
        self.group_box = QtWidgets.QGroupBox(title)
        self.group_layout = QtWidgets.QVBoxLayout()
        self.group_box.setLayout(self.group_layout)
        self.inner_block = inner_block_type()
        self.group_layout.addWidget(self.inner_block)
        self._layout.addWidget(self.group_box)

    @property
    def outer_layout(self):
        return self._layout

    def zero_outer_margins(self):
        self.outer_layout.setContentsMargins(0, 0, 0, 0)

    @property
    def layout(self):
        return self.inner_block.layout

    @property
    def title(self):
        return self.group_box.title()

    @title.setter
    def title(self, title: str):
        self.group_box.setTitle(title)

    @property
    def collapsible(self):
        return self.group_box.isCheckable()

    @collapsible.setter
    def collapsible(self, collapsible: bool):
        self.group_box.setCheckable(collapsible)

    @property
    def collapsed(self):
        return not self.group_box.isChecked()

    @collapsed.setter
    def collapsed(self, collapsed: bool):
        self.group_box.setChecked(not collapsed)


class VGroupBlock(GroupBlock):
    """A Block with an embedded vertical group box."""

    def __init__(self, title: t.Optional[str], parent=None):
        super().__init__(VBlock, title, parent)


class HGroupBlock(GroupBlock):
    """A Block with an embedded horizontal group box."""

    def __init__(self, title: t.Optional[str], parent=None):
        super().__init__(HBlock, title, parent)


class FlowGroupBlock(GroupBlock):
    """A Block with an embedded flow group box."""

    def __init__(self, title: t.Optional[str] = None, parent=None):
        super().__init__(FlowBlock, title, parent)


class _ScrollGroupBlock(GroupBlock):
    """A Block with an embedded scroll group box.

    This class should not be instantiated directly.  Instead, use one of the
    ScrollGroupBlock subclasses or create a new subclass.
    """

    def __init__(self, inner_block_type, title: t.Optional[str] = None, parent=None):
        super().__init__(inner_block_type, title, parent)

    def always_show_scrollbar(self):
        self.inner_block.always_show_scrollbar()  # type: ignore


class VScrollGroupBlock(_ScrollGroupBlock):
    """A Block with an embedded vertical scroll group box."""

    def __init__(self, title: t.Optional[str] = None, parent=None):
        super().__init__(VScrollBlock, title, parent)


class HScrollGroupBlock(_ScrollGroupBlock):
    """A Block with an embedded horizontal scroll group box."""

    def __init__(self, title: t.Optional[str] = None, parent=None):
        super().__init__(HScrollBlock, title, parent)


class FlowScrollGroupBlock(_ScrollGroupBlock):
    """A Block with an embedded flow scroll group box."""

    def __init__(self, title: t.Optional[str] = None, parent=None):
        super().__init__(FlowScrollBlock, title, parent)
