# **3D Object Viewer**

This project uses PySide6 and Python to build a 3D object viewer within 2 days. This was fun, prior to this I had no experience with PySide6.

To launch, run `python main.py` in the root directory.

## Requirements

| Component | Description | Status |
| --- | --- | --- |
| Scene Rendering | A 3D viewer that shows objects in the 3D environment | Completed |
| Camera Control | Able to navigate the 3D environment moving up, down, left, right, forward, backward <br> Able to rotate around a point <br> See [QOrbitCameraController](https://doc.qt.io/qtforpython-6/PySide6/Qt3DExtras/QOrbitCameraController.html) for full list of controls. | Completed |
| Object Management | Able to create primitives box and sphere to the environment <br> Able to delete object in the environment <br> Able to list all objects in the environment | Completed |
| Object Editing | Able to change the name of the object by modifying the name attribute <br> Able to change the color of the drawable by modifying the color attribute <br> Able to change position and orientation of object by modifying model attributes | Completed |
| Data Management | Store model attributes in local storage (as JSON) <br> Should be able to resume the app from shutdown or unexpected crashing | Completed |

## Bonus Features

| Feature | Description | Status |
| --- | --- | --- |
| Dragging to Change Position | Allow clicking and dragging of drawables to change their position or orientation. <br> (Currently only able to drag in a 2D plane, no rotation.) | In Progress |
| Click to Select Object | Click to select object in viewer and jump to corresponding item in the object list, | Completed |
| Record Editing History | Record editing history of your objects, can undo and redo changes to an object. <br> (However, dragging and adding/deleting objects is not yet supported.) | Completed |
| Import STL File | Support creating object of any shape by import stl file <br> (Currently only able to do this programatically, no UI yet. Edit file path in constants.py) | In Progress |
| Support Hierarchy | Support hierarchy. a.k.a support nested object. <br> (This would require supporting parent child relationships like such ``sphereB = Qt3DCore.QEntity(boxA)`` and having the UI handle the display through a tree-like structure in the widget list and allowing the user to select a parent when editing the object.) | Not Started |
| Custom Shader | Have custom shader(s) to mimic shading in Solidworks (edge outlines) | Not Started |

## Structure

The project has the following structure:
```plaintext
.
├── src
│   ├── command.py          # Track commands for undo/redo
│   ├── constants.py        # Constants like scale factor
│   ├── editWindow.py       # UI for the editing of objects
│   ├── entityObject.py     # Define an object class
│   ├── mainWindow.py       # UI for rendering the main window - 3D frame and edit window and list interface
│   └── userInterface.py    # UI for where user interactions take place, adding/deleting objects, etc.
├── stl
│   ├── car.stl             # Test STL file
│   └── test.stl            # Test STL file
└── entities.json           # Local storage of saved entities
```

## Resources

The following resources were used in the development of this application:

- [Qt for Python Documentation](https://doc.qt.io/qtforpython-6/quickstart.html)
- [PySide6 Widgets Tutorial](https://www.pythonguis.com/tutorials/pyside6-widgets/)
- [YouTube Video Tutorial](https://www.youtube.com/watch?v=dpj2dZQA63c)

Huge thanks to Copilot for the generation of Docstrings/comments. 