from manim import *


class Grid(VGroup):
    CONFIG = {
        "rows": 8,
        "columns": 14,
        "grid_height": config.frame_height,
        "grid_width": config.frame_width,
        "grid_stroke": 0.5,
        "grid_color": WHITE,
        "axis_color": RED,
        "axis_stroke": 2,
        "labels_scale": 0.6,
        "labels_buff": 0,
        "number_decimals": 1,
        "show_labels": False,
    }

    def __init__(self, rows, columns, **kwargs):
        for key in self.__class__.CONFIG:
            setattr(self, key, self.__class__.CONFIG.get(key))
        self.rows = rows
        self.columns = columns
        super().__init__(**kwargs)

        x_step = self.grid_width / self.columns
        y_step = self.grid_height / self.rows

        for x in np.arange(0, self.grid_width + x_step, x_step):
            self.add(Line(
                [x - self.grid_width / 2., -self.grid_height / 2., 0],
                [x - self.grid_width / 2., self.grid_height / 2., 0],
            ))
        for y in np.arange(0, self.grid_height + y_step, y_step):
            self.add(Line(
                [-self.grid_width / 2., y - self.grid_height / 2., 0],
                [self.grid_width / 2., y - self.grid_height / 2., 0]
            ))

    def get_axes(self):
        """Get the two axes lines"""
        pass

    def add_lines(self):
        """Add lines to VGroup"""
        endpoints = [[LEFT * config.frame_x_radius, RIGHT * config.frame_x_radius],
                     [DOWN * config.frame_y_radius, UP * config.frame_y_radius]]
        lines_range = [config.frame_width, config.frame_height]
        steps = [config.frame_width / self.columns, config.frame_height / self.rows]
        for line_ends, dim, step in zip(endpoints, lines_range, steps):

            for pos in np.arange(0, dim + step, step):
                start = [np.array([pos, 0, 0]) + line_ends[0]]
                end = line_ends[0]
                self.add(Line(*line_ends))

        pass


class ScreenGrid(VGroup):
    CONFIG = {
        "rows": 8,
        "columns": 14,
        "grid_height": config.frame_height,
        "grid_width": config.frame_width,
        "grid_stroke": 0.5,
        "grid_color": WHITE,
        "axis_color": PURPLE,
        "axis_stroke": 2,
        "labels_scale": 0.6,
        "labels_buff": 0,
        "number_decimals": 1,
        "show_labels": False,
    }

    def __init__(self, **kwargs):
        for key in self.__class__.CONFIG:
            setattr(self, key, self.__class__.CONFIG.get(key))
        super().__init__(**kwargs)
        rows = self.rows
        columns = self.columns
        grid = Grid(rows=rows,
                    columns=columns)
        grid.set_stroke(self.grid_color, self.grid_stroke)

        vector_ii = ORIGIN + np.array((- self.grid_width / 2, - self.grid_height / 2, 0))
        vector_si = ORIGIN + np.array((- self.grid_width / 2, self.grid_height / 2, 0))
        vector_sd = ORIGIN + np.array((self.grid_width / 2, self.grid_height / 2, 0))

        axes_x = Line(LEFT * self.grid_width / 2, RIGHT * self.grid_width / 2)
        axes_y = Line(DOWN * self.grid_height / 2, UP * self.grid_height / 2)

        axes = VGroup(axes_x, axes_y).set_stroke(self.axis_color, self.axis_stroke)

        divisions_x = self.grid_width / columns
        divisions_y = self.grid_height / rows

        directions_buff_x = [UP, DOWN]
        directions_buff_y = [RIGHT, LEFT]
        dd_buff = [directions_buff_x, directions_buff_y]
        vectors_init_x = [vector_ii, vector_si]
        vectors_init_y = [vector_si, vector_sd]
        vectors_init = [vectors_init_x, vectors_init_y]
        divisions = [divisions_x, divisions_y]
        orientations = [RIGHT, DOWN]
        labels = VGroup()
        set_changes = zip([columns, rows], divisions, orientations, [0, 1], vectors_init, dd_buff)
        for c_and_r, division, orientation, coord, vi_c, d_buff in set_changes:
            for i in range(1, c_and_r):
                for v_i, directions_buff in zip(vi_c, d_buff):
                    ubication = v_i + orientation * division * i
                    coord_point = round(ubication[coord], self.number_decimals)
                    label = Text(f"{coord_point}",font="Arial", stroke_width=0).scale(self.labels_scale)
                    label.next_to(ubication, directions_buff, buff=self.labels_buff)
                    labels.add(label)

        if self.show_labels:
            self.add(grid, axes, labels)

        else:
            self.add(grid, axes)

    def get_axes(self):
        """Get the x and y axes"""
        pass


class CoordScreen(Scene):
    def construct(self):
        screen_grid = ScreenGrid()
        dot = Dot([1, 1, 0])
        self.add(screen_grid)
        self.play(FadeIn(dot))
        self.wait()
