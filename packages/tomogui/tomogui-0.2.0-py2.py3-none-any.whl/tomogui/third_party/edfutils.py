from fabio.edfimage import edfimage
import os

def decreaseMatSize(mat):
    """
    will decrease the matrice size if possible where one dimension has only
    one element
    """
    if (len(mat.shape) == 3):
        if (mat.shape[0] == 1):
            mat.shape = (mat.shape[1], mat.shape[2])
        elif (mat.shape[2] == 1):
            mat.shape = (mat.shape[0], mat.shape[1])

    if (len(mat.shape) == 4):
        if (mat.shape[0] == 1):
            mat.shape = (mat.shape[1], mat.shape[2], mat.shape[3])
        if (mat.shape[3] == 1):
            mat.shape = (mat.shape[0], mat.shape[1], mat.shape[2])

    return mat


def saveMatrix(data, fileName, overwrite=False):
    """
    will create an edf file to store the given data

    :param data: the data to save
    :param fileName: the localisation to know where to save the data
    """
    if (os.path.isfile(fileName)):
        if overwrite is True:
            logger.info("overxtriting the file : " + str(fileName))
        else:
            logger.info("file " + str(fileName) + "already exists")
            return

    phantomToSave = data.copy()
    phantomToSave = decreaseMatSize(phantomToSave)
    edf_writer = edfimage(data=phantomToSave)
    edf_writer.write(fileName)
    edf_writer = None


def LoadEdf_2D(fName, frame=0):
    """
    Load data from the given edf file

    :param fName: the name of the file
    :param frame: if multiple frame file, will use theis parameter to load a
                  specific frame
    """
    edfreader = edfimage()
    edfreader.read(fName)
    if edfreader.nframes == 1:
        return edfreader.getData()
    else:
        return edfreader.getframe(frame)