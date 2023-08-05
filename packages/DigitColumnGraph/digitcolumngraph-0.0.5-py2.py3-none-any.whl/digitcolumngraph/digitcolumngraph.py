from math import ceil

class DigitColumnGraph:
    max_height = 15
    max_title_width = 30
    spacing = 2

    items = {}
    value_char = '#'

    def width(self):
        return (self.spacing * (len(self.items) - 1)) + (len(self.items) * self.col_width())

    def height(self):
        diff = self.scale()[1] - self.scale()[0]
        return ceil(diff / self.scale()[2])

    def col_width(self):
        result = 0
        for key, value in self.items.items():
            if len(str(key)) > result:
                result = len(str(key))
        return result if result < self.max_title_width else self.max_title_width

    def scale(self):
        min = 0
        max = 0
        for key, value in self.items.items():
            if value > max:
                max = value
            elif value < min:
                min = value

        step = 1
        if (max - min) > self.max_height:
            step = ceil((max - min) / self.max_height)

        return (min,max,step)

    def _draw_titles(self):
        result = []
        for key, value in self.items.items():

            for index, char in enumerate(key):

                if index != self.col_width():
                    result.append(char)

                else: #add elipse to title if it is longer then max_title_width
                    del result[len(result) - 3:len(result)]
                    result.extend(['.', '.', '.'])
                    break

            #fill title with whitespace to match self.col_width() and add between spacing
            while len(result) % (self.col_width() + self.spacing) != 0:
                if len(result) == self.width():
                    break
                result.append(' ')

        return ''.join(result)

    def _draw_values(self):
        res = []
        for i in range(self.height()):
            res.append([])
            for z in range(self.width()):
                res[i].append(' ')

        key_index = 0
        for key, value in self.items.items():

            for i in range(self.height()):
                cap  = (i + 1) * self.scale()[2]
                if value >= cap:
                    res[i][(key_index * self.col_width()) + (key_index * self.spacing)] = self.value_char
                else:
                    break

            key_index = key_index + 1

        for index, item in enumerate(res):
            res[index] = ''.join(item)
        res.reverse()

        return res

    def _draw_scale(self):
        result = []
        for i in range(self.height()):
            result.append(str((i + 1) * self.scale()[2]))
        result.reverse()
        return result

    def draw(self):
        scale = self._draw_scale()
        values = self._draw_values()
        titles = self._draw_titles()

        res = []
        for index, val in enumerate(scale):
            res.append(val + ' ' * (len(str(self.scale()[1])) - len(str(val))) + ' ' * self.spacing + values[index])
        res.append(' ' * len(str(self.scale()[1])) + ' ' * self.spacing + titles)

        return res

    def __init__(self, items, value_char = '#'):
        self.items = items
        self.value_char = value_char
