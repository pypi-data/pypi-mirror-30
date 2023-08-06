from PIL import Image, ImageDraw, ImageFont
import pickle
import sys
import numpy as np

CHARACTERS = ''.join([chr(x) for x in range(32, 127)])


class LetterBitmapDictionary:
    """ Generates and stores a dictionary object containing character key with binary tuple data representing the
    pixels of the letter when drawn in the specified font.
    """
    def __init__(self, font, size, data_folder, maxy=sys.maxsize, maxx=sys.maxsize, use_save=True, transposed=False):
        """ LetterBitmapDictionary
        :param font: path to font
        :param size: size to draw font (affects canvas size)
        :param data_folder: path to folder where the dictionary can be saved for later use
        :param maxy: crop the image vertically by pixels
        :param maxx: crop the image horizontally by pixels
        :param use_save: enable/disable saving the dictionary
        :param transposed: flip rows/cols of tuple
        """
        self.data_folder = data_folder
        self.font = ImageFont.truetype(font, size)
        self.name = ''.join(self.font.getname())
        self.chardict = {}
        if use_save:
            try:
                self.load()
            except IOError:
                self._createdic(maxx, maxy, transposed)
                self.save()
        else:
            self._createdic(maxx, maxy, transposed)

    def _createdic(self, maxx, maxy, transpose):
        for c in CHARACTERS:
            fontsize = self.font.getsize(c)
            imagesize = (min(fontsize[0], maxx), min(fontsize[1], maxy))
            image = Image.new('1', imagesize)
            drawer = ImageDraw.Draw(image)
            drawer.text((0, 0), c, font=self.font, fill=1)
            nparr = np.asarray(image)
            if transpose:
                nparr = nparr.T
            self.chardict[c] = tuple(map(tuple, nparr))

    def load(self):
        """ Load font from file. """
        with open(self.data_folder + self.name + '.pkl', 'rb') as data_folder:
            self.chardict = pickle.load(data_folder)

    def save(self):
        """ Save font to file. """
        with open(self.data_folder + self.name + '.pkl', 'wb') as data_folder:
            pickle.dump(self.chardict, data_folder, pickle.HIGHEST_PROTOCOL)

    def __getitem__(self, item):
        return self.chardict[item]

    def __repr__(self):
        print(self.name)

    def __str__(self):
        output = ''
        for c in CHARACTERS:
            output += '\n' + "'" + c + "'"
            for t in self.chardict[c]:
                output += '\n'
                for b in t:
                    output += '#' if b else '-'

        return output
