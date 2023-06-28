# Blocks!

Qt-Blocks reduce GUI boilerplate for complex tools.

Each `block` is a QFrame pre-populated with a layout and other child widgets.

For example, to create a scrollable block with a vertical layout and 2 buttons:

```python
block = VScrollBlock()
block.align_top()
block.widgets = [QPushButton("Button 1"), QPushButton("Button 2")]
```

The equivalent code without using blocks would be::

```python
scroll_area = QScrollArea()
scroll_widget = QFrame()
scroll_layout = QVBoxLayout()
scroll_layout.setAlignment(Qt.AlignTop)
scroll_layout.addWidget(QPushButton("Button 1"))
scroll_layout.addWidget(QPushButton("Button 2"))
scroll_widget.setLayout(scroll_layout)
scroll_area.setWidgetResizable(True)
scroll_area.setWidget(scroll_widget)
```

This boilerplate reduction adds up significantly when building large, complex
tools with nested components and layouts.

Blocks can generally also be used as replacements for layouts, if the initial
margins and spacing are set to 0.  One benefit of this approach is that blocks
are styleable with QSS, while layouts are not.

# Layouts!

This package also includes two custom layout types, `FlowLayout` and `ColumnLayout`.

# FlowLayout
The `FlowLayout` arranges widgets based on available horizontal space. When the width of the layout is exceeded, the rest of the widgets are moved to the next line. This is useful for creating dynamic user interfaces that adapt to the size of the window or the available space.

# ColumnManager / ColumnLayout
The `ColumnManager` class is a helper class for managing widgets organized into columns.  Given a number of `ColumnLayout` instances, the ColumnManager will unify the widths of widgets in each column of each layout.  Importantly, the managed layouts do not need to be *contiguous*.

## Usage
Here is an example of how to use the ColumnLayout and ColumnManager classes:

```python
from PySideCustomLayouts import ColumnManager, ColumnLayout
from qtpy import QtWidgets

manager = ColumnManager()
row_one = QtWidgets.QFrame()
row_one.setLayout(ColumnLayout(manager))
interruption = QtWidgets.QLabel("==============")
row_two = QtWidgets.QFrame()
row_two.setLayout(ColumnLayout(manager))

row_one.layout().addWidget(QtWidgets.QLabel("spam"))
row_one.layout().addWidget(QtWidgets.QPushButton("eggs"))
row_two.layout().addWidget(QtWidgets.QLabel("baked beans"))
row_two.layout().addWidget(QtWidgets.QPushButton("and spam"))

parent_widget.addWidget(row_one)
parent_widget.addWidget(interruption)
parent_widget.addWidget(row_two)
```

This example lays out the widgets like this:

```
[spam       ]| [eggs    ]
=========================
[baked beans]| [and spam]
```
The columns of the two rows are aligned, even though they are not part of the same `Layout`.

## Controlling column widths

By default, each column's width is based on the minimum width hint of the largest item in that column (so for the example above, "baked beans" is the widest widget, so that determines the width of the column).

You can set a fixed width for specific columns by using the `column_widths` dictionary of the `ColumnManager`:
```python
manager.column_widths[0] = 100
```

You can also tell individual columns to automatically stretch to fill available space.  This is handled through the `stretch_columns` list attribute on `ColumnManager`:
```python
manager.stretch_columns = [1, 3]
```
