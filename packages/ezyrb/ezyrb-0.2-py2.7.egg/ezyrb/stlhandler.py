"""
Module to handle STL files.
"""
import os
import numpy as np
import vtk


class StlHandler(object):
    """
    Vtk format file handler class.
    You are NOT supposed to call directly this class constructor (use
    :class:`~.FileHandler` constructor instead)

    :param str filename: name of file

    :cvar str _filename: name of file to handle
    :cvar vtkPolyData _cached_data: private attribute to store the last
        polydata processed
    """

    def __init__(self, filename):
        self._filename = filename
        self._cached_data = None

    def _read_polydata(self):
        """
        This private method reads the given `filename` and return a vtkPolyData
        object containing all informations about file; to avoid useless IO
        operation on the same file, it stores polydata of the last file parsed
        and if user ask for this file, the polydata previously stored is
        returned.

        :return: polydata containing information about file.
        :rtype: vtkPolyData
        """
        # Polydata from `filename` is already loaded; return it
        if self._cached_data is not None:
            return self._cached_polydata

        if not os.path.isfile(self._filename):
            raise RuntimeError("{0!s} doesn't exist".format(
                os.path.abspath(self._filename)))

        reader = vtk.vtkSTLReader()
        reader.SetFileName(self._filename)
        reader.Update()
        data = reader.GetOutput()

        self._cached_data = data

        return data

    def _save_polydata(self, data, write_bin=False):
        """
        This private method saves into `filename` the `data`. `data` is a
        vtkPolydata. It is possible to specify format for `filename`: if
        `write_bin` is True, file is written in binary format, otherwise in
        ASCII format. This method save cached polydata to reduce number of IO
        operations.

        :param vtkPolyData data: polydatat to save.
        :param bool write_bin: for binary format file.
        """
        self._cached_data = data

        writer = vtk.vtkSTLWriter()

        if write_bin:
            writer.SetFileTypeToBinary()

        writer.SetFileName(self._filename)

        if vtk.VTK_MAJOR_VERSION <= 5:
            writer.SetInput(data)
        else:
            writer.SetInputData(data)
        writer.Write()

    def get_geometry(self, get_cells=False):
        """
        This method reads the given `filename` and returns points and cells of
        file. If `get_cells` is True, it computes the list that contain index of
        points defining cells, otherwise the list is not computed and set to
        **None** (less expensive).

        :param bool get_cells: flag to compute cells list or not. Default is
            false.

        :return: the `n_points`-by-3 matrix containing the coordinates of the
            points, the n_cells list containing, for each cell, the index of
            the points that define the cell (if computed).
        :rtype: numpy.ndarray, list(numpy.ndarray) or None
        """
        data = self._read_polydata()

        n_points = data.GetNumberOfPoints()
        n_cells = data.GetNumberOfCells()

        points = np.array([data.GetPoint(i) for i in np.arange(n_points)])
        cells = None

        if get_cells:
            cells = [[
                data.GetCell(i).GetPointIds().GetId(idx)
                for idx in np.arange(data.GetCell(i).GetNumberOfPoints())
            ] for i in np.arange(n_cells)]

        return points, cells

    def set_geometry(self, points, cells, write_bin=False):
        """
        This method save into `filename` a new data defined by `points` and
        `cells`.

        :param numpy.ndarray points: matrix *n_points*-by-3 containing
            coordinates of all points.
        :param list(list(int)) cell: a list of lists that contains, for each
            cell, the index of points defining the cell.
        :param bool write_bin: flag to write in the binary format. Default is
            false.
        """
        data = vtk.vtkPolyData()
        vtk_points = vtk.vtkPoints()
        vtk_cells = vtk.vtkCellArray()

        for i in np.arange(points.shape[0]):
            vtk_points.InsertNextPoint(points[i])

        for i in np.arange(len(cells)):
            vtk_cells.InsertNextCell(len(cells[i]), cells[i])

        data.SetPoints(vtk_points)
        data.SetPolys(vtk_cells)

        self._save_polydata(data, write_bin)
