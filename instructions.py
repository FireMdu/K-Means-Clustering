from manim import *


class ExplainKMeans(Scene):
    def construct(self):
        self.pull_up_rectangle_screen()
        self.wait()
        self.next_section()
        self.instructions = [
            Text("Randomly choose K data points from the given data points", font='Chiller'),
            Text("Randomly choose K data points from the given data points", font='Chiller')
        ]
        goal = MarkupText('The goal is to form '
                          '<gradient from="BLUE" to="YELLOW">k groups/classes</gradient> '
                          'from the datapoints', font='Chiller')
        # BulletedList
        goal.scale(0.7).next_to(self.view_screen, DOWN, buff=0.1, aligned_edge=LEFT)

        similarity = MarkupText(
            'The points are grouped based on some '
            '<gradient from="YELLOW" to="RED">similarity measure</gradient>', font='Chiller')
        similarity.scale(0.7).next_to(goal, DOWN, buff=0.2, aligned_edge=LEFT)
        # The goal is to form k groups/classes from the datapoints
        # The points are grouped based on some similarity measure
        similarity_measure = MarkupText('In this demo, that similarity measure '
                                  'is the <span color="aquamarine">distance from \na group centre</span>',
                                  font='Chiller')
        similarity_measure.scale(0.7).next_to(similarity, DOWN, aligned_edge=LEFT, buff=0.2)
        groups = VGroup(*[goal, similarity, similarity_measure])
        self.next_section(skip_animations=True)
        self.play(FadeIn(goal), run_time=1.6)
        self.wait(2)
        self.play(Write(similarity))
        self.wait(2)
        self.play(FadeIn(similarity_measure), run_time=1.6)
        self.wait(2)
        self.play(
            groups.animate.scale(0.6).to_corner(UL, buff=0.1),
            lag_ratio=0.7, rate_func=rush_into, run_time=1.3)
        self.wait()
        groups.save_state()

        self.next_section()
        steps = Text('Steps/Algorithm').scale(0.5)
        steps.next_to(groups, DOWN, aligned_edge=LEFT, buff=0.7)
        underline_steps = Line(stroke_width=1)
        underline_steps.match_width(steps).next_to(steps, DOWN, buff=0)
        self.play(AnimationGroup(*[Write(steps), Write(underline_steps), groups.animate.fade(0.95)]), lag_ratio=0.7)
        self.wait()

        choose_start_center = Text('1. Randomly select k points from the dataset.\n   These will be '
                                   'the initial group centers.', font='Consolas').scale(0.3)

        assign_points_to_group = Text("2. Assign each datapoint in the dataset to "
                                      "\n   the closet group center", font='Consolas').scale(0.3)
        get_new_mean = Text("3. Get each group's mean value and make \n   it the new group center", font='Consolas').scale(0.3)
        iterate_task = Text("4. Perform the above two steps until the new \n   group center is the same as the previously "
                           "\n   calculated group center", font='Consolas').scale(0.3)

        choose_start_center.next_to(steps, DOWN, aligned_edge=LEFT, buff=0.1)
        assign_points_to_group.next_to(choose_start_center, DOWN, aligned_edge=LEFT, buff=0.1)
        get_new_mean.next_to(assign_points_to_group, DOWN, aligned_edge=LEFT, buff=0.1)
        iterate_task.next_to(get_new_mean, DOWN, aligned_edge=LEFT, buff=0.1)
        self.play(Write(choose_start_center))
        self.wait(2)
        self.play(Write(assign_points_to_group))
        self.wait(2)
        self.play(Write(get_new_mean))
        self.wait(2)
        self.play(Write(iterate_task))
        self.wait()

    def pull_up_rectangle_screen(self):
        self.view_screen = ScreenRectangle(stroke_width=1)
        self.view_screen.scale(1.25).to_corner(UR, buff=0.1)
        self.play(Write(self.view_screen))

    def show_current(self, index):
        instruct = self.instructions[index]
        instruct.to_corner(DL, buff=0.3)
        self.play(Write(instruct))

    def move_to_static_position(self, index):
        if index == 0:
            position = UL
            func = "to_corner"
        else:
            position = DOWN
            func = "next_to"

        instruct = self.instructions[index]
        instruct.generate_target()
        setattr(instruct.target, func, position)
        self.play(ReplacementTransform(instruct, instruct.target))


class KMeansIntro(Scene):
    def construct(self):
        kmeans_intro = MarkupText('<gradient from="BLUE" to="YELLOW">K-Means</gradient> Clustering', font="Trajan Pro")
        kmeans_def = MarkupText('A process of grouping data-points of a dataset into '
                                '<gradient from="BLUE" to="YELLOW">k groups</gradient> '
                                'based \non the "distance" of the datapoint to the '
                                '<gradient from="BLUE" to="YELLOW" offset="1">group means</gradient>.').scale(0.35)
        kmeans_def.next_to(kmeans_intro, DOWN, aligned_edge=LEFT, buff=0.1).shift(0.6*RIGHT)

        self.play(Write(kmeans_intro), lag_ratio=0.7, rate_fun=rush_into)
        self.wait()
        self.play(Write(kmeans_def), lag_ratio=0.7, run_time=6, rate_func=rush_into)

        self.wait()


class Notes(Scene):
    def construct(self):
        notes_header = Text("Some Notes:").scale(0.6)
        notes_header.to_corner(UL, buff=1)
        notes_underline = Line(stroke_width=1, color=PURPLE)
        notes_underline.stretch_to_fit_width(notes_header.width).next_to(notes_header, DOWN, buff=0.1)

        dimensions = Text(
            "- The algorithm can be extended for any \n  number of datapoint dimensions.", font='Consolas').scale(0.3)
        dimensions.next_to(notes_header, DOWN, buff=0.45, aligned_edge=LEFT)
        center_purpose = Text("- Properties of the center/mean of the "
                              "group \n  represent the properties of the group.",
                              font='Consolas'
                              ).scale(0.3)
        center_purpose.next_to(dimensions, DOWN, buff=0.15, aligned_edge=LEFT)
        euclidean = Text("- For datapoints defined on a Euclidean space the, \n  Euclidean distance "
                         "is the similarity measure.", font='Consolas').scale(0.3)
        euclidean.next_to(center_purpose, DOWN, buff=0.15, aligned_edge=LEFT)

        initial_centers = Text("- The choice of the initial centers determines how long "
                               "\n  it takes the algorithm to converge to a solution.", font='Consolas').scale(0.3)
        initial_centers.next_to(euclidean, DOWN, buff=0.15, aligned_edge=LEFT)
        self.wait(2)
        self.play(FadeIn(notes_header), Write(notes_underline))
        self.wait()
        self.play(FadeIn(dimensions))
        self.wait()
        self.play(Write(center_purpose))
        self.wait()
        self.play(Write(euclidean))
        self.wait()
        self.play(FadeIn(initial_centers))
        self.wait()
