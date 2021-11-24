from manim import *
from submodules.cluster import SKLearnKMeans, generate_vertices, KMeans, PointCoord
from submodules.screen_grid import ScreenGrid
import itertools as it
import random as rnd


class KMeansScene(Scene):

    def setup(self):
        """All necessary variable initialization"""
        self.points = generate_vertices(60, 4, seed=150)
        self.num_clusters = 3
        self.kmeans = KMeans(self.points, self.num_clusters)
        self.grid = ScreenGrid()

    def construct(self):
        """Animations to run"""
        self.post_set_up()
        self.wait()
        self.play(FadeIn(self.dots_group))
        self.play(Write(self.grid))
        self.wait(2)
        self.next_section()
        self.play(*self.initialize_centers(), run_time=3, rate_func=slow_into)
        self.wait(2)
        self.next_section()
        for _ in self.kmeans.iterate_cluster(200):
            for cluster_key in self.kmeans.clusters_dictionary:
                self.play(self.set_cluster_color(cluster_key))
                self.wait()
            for cluster_key in self.kmeans.clusters_dictionary:
                self.play(
                    self.update_cluster_center_object(cluster_key),
                    run_time=3, rate_func=slow_into)
            self.play(*self.reset_clusters())
            self.wait(1.2)
        for cluster_key in self.kmeans.clusters_dictionary:
            self.play(self.set_cluster_color(cluster_key))
            self.wait()

        self.next_section()
        self.play(
            AnimationGroup(*[Indicate(self.centers[key], scale_factor=2.5) for key in range(len(self.centers))]),
            lag_ratio=0.7
        )
        self.wait(2)

    def post_set_up(self):
        self.cluster_colors = self.clusters_color_range
        self.colors_dictionary = self.colors_dict
        self.centers = self.get_center_objects
        dots = list(it.chain(*self.get_point_objects.values()))
        rnd.shuffle(dots)
        self.dots_group = VGroup(*dots)

    def resize_screen(self, width):
        """Resize screen ratio"""
        pass

    @property
    def colors_dict(self):
        return {key: value for key, value in enumerate(self.cluster_colors)}

    @property
    def clusters_color_range(self):
        """Return list of colors interpolated between supplied colors"""
        return color_gradient([BLUE, GREEN, ORANGE, PURPLE, YELLOW],
                              len(self.kmeans.clusters_dictionary))

    @property
    def get_point_objects(self, scale=0.5):
        """Map a coordinate tuple to object position"""
        return {coord: Dot(color=GREY, point=point.point_to_np,
                           radius=0.2).scale(scale) for coord, point in
                self.kmeans.points_dictionary.items()}

    def get_cluster_points(self):
        """Return current cluster state"""
        return {key: cluster.points for key, cluster in
                self.kmeans.clusters_dictionary.items()}

    def get_cluster_group(self, cluster_key):
        """Return a Vector Group of cluster objects"""
        # get cluster instance
        cluster_instance = self.kmeans.clusters_dictionary[cluster_key]
        # group objects of cluster
        return VGroup(*[obj for obj in self.dots_group if PointCoord(
            *obj.get_center()) in cluster_instance.points])

    def set_cluster_color(self, cluster_key):
        """Set color of cluster objects"""
        # get cluster color
        color = self.cluster_color(cluster_key)
        # get cluster group
        cluster_group = self.get_cluster_group(cluster_key)
        # apply color method to group
        return ApplyMethod(cluster_group.set_color, color)

    def reset_clusters(self):
        """Reset clusters"""
        return [ApplyMethod(obj.set_color, GREY) for obj in
                self.dots_group]

    @staticmethod
    def center_object(color, scale=0.5):
        """Return center objects"""
        return Dot(radius=0.3).set_fill(color=color, opacity=0.3).scale(scale)

    def cluster_color(self, cluster_key):
        """Return cluster color"""
        return self.colors_dictionary[cluster_key]

    @property
    def get_center_objects(self):
        """Return a dictionary of all cluster centers with their colors"""
        return {key: self.center_object(color) for key, color
                in self.colors_dictionary.items()}

    def update_cluster_center_object(self, cluster_key):
        """Move cluster center mark to new cluster center"""
        return ApplyMethod(self.centers[cluster_key].move_to,
                           self.kmeans.clusters_dictionary[
                               cluster_key].center.point_to_np)

    def initialize_centers(self):
        """move all cluster centers to their initial positions"""
        move_centers = [ApplyMethod(self.centers[cluster_key].move_to,
                                    self.kmeans.clusters_dictionary[
                                        cluster_key].center.point_to_np) for
                        cluster_key in self.kmeans.clusters_dictionary.keys()]
        return move_centers

    def get_center_coords(self, cluster_key):
        """Get coordinates of the cluster center"""
        center = self.centers[cluster_key]
        return center.get_x(), center.get_y()

    def get_centers(self):
        self.center_coords = {key: DecimalNumber().set_color(
            self.cluster_color(key)) for key in self.kmeans.clusters_dictionary}

    def update_center_coords(self, key):
        self.center_coords[key].add_updater(lambda d: d.set_value(
            self.get_center_coords(key)))

    def introduce_data(self, data, animation):
        """Introduce data to be clustered"""
        self.play(animation(data), run_time=6, rate_func=rush_from)


class AssignPoint(KMeansScene):
    def construct(self):
        self.play(Write(self.grid))
        self.post_set_up()
        self.play(FadeIn(self.dots_group))
        self.play(*self.initialize_centers())

        # get all lines from each cluster to each of the points
        self.lines = [self.group_point_cluster_lines(point) for point in
                      self.dots_group]
        self.ref_lines_group = self.lines[0]

        # get initial distances dictionary
        self.get_distances()
        self.set_update_all_cluster_distances()

        # add updaters for all lines
        display_distances = VGroup(*self.distances.values()).arrange(RIGHT,
                                                                     buff=0.9*self.camera.frame_width/self.num_clusters)
        display_distances.to_edge(DOWN, buff=0.2)

        index = 0
        # fade in lines from cluster centers to first point
        self.wait(2)
        self.add(display_distances)
        self.wait(2)
        for index, point in enumerate(self.dots_group):
            min_line = self.get_shortest_distance(point)

            # manipulate updaters
            def manipulate_updaters():
                self.suspend_all_cluster_distance_updaters()
                self.play(self.wiggle_minimum(min_line))
                self.wait(0.1)
                self.play(self.classify_point(self.dots_group[index],
                                              min_line), run_time=0.4)
                self.resume_all_cluster_point_distance_updaters()

            if index == 0:
                self.play(Write(self.ref_lines_group), run_time=3)
                manipulate_updaters()
                pass
            else:
                self.play(Transform(self.ref_lines_group, self.lines[index]))
                manipulate_updaters()
        self.wait(1)

    def pick_points(self, k):
        """pick k points from a sample"""
        return rnd.sample(list(self.dots_group), k)

    def draw_lines(self, point):
        """Return a dictionary of distance lines with keys as cluster keys"""
        lines = {key: Line(point.get_center(), cluster.center.point_to_np, stroke_width=1)
                 for key, cluster in self.kmeans.clusters_dictionary.items()}
        [(line.set_color(color=self.colors_dictionary[key])) for key, line in
         lines.items()]
        return lines

    def group_point_cluster_lines(self, point):
        """Return a list of lines drawn for each point in space from the
        cluster centers to a point"""
        return VGroup(*self.draw_lines(point).values())

    def get_shortest_distance(self, point):
        """Return shortest distance from the cluster point line"""
        lines = self.draw_lines(point)
        return min(lines.keys(), key=(lambda d: lines[d].get_length()))

    def get_distances(self):
        """Get a dictionary of distances with keys as cluster keys"""
        self.distances = {key: DecimalNumber().scale(0.5).set_color(self.cluster_color(
            key)) for key in self.kmeans.clusters_dictionary}

    def update_cluster_point_distance(self, key):
        """Update each distance to the cluster from point"""
        self.distances[key].add_updater(
            lambda d: d.set_value(self.ref_lines_group.submobjects[
                                      key].get_length()))

    def suspend_cluster_point_distance_updater(self, key):
        # remove updater of cluster-point line
        self.distances[key].suspend_updating()

    def resume_cluster_point_distance_updater(self, key):
        # resume updater of all cluster-point lines
        self.distances[key].resume_updating()

    def resume_all_cluster_point_distance_updaters(self):
        [self.resume_cluster_point_distance_updater(key) for key in
         self.kmeans.clusters_dictionary]

    def set_update_all_cluster_distances(self):
        """Update all cluster to point distances"""
        for key in self.kmeans.clusters_dictionary:
            self.update_cluster_point_distance(key)

    def suspend_all_cluster_distance_updaters(self):
        """remove all cluster to point distances updaters"""
        [self.suspend_cluster_point_distance_updater(key) for key in
         self.kmeans.clusters_dictionary]

    def initialize_centers(self):
        """move all cluster centers to their initial positions and fade them
        in from there"""
        for cluster_key in self.kmeans.clusters_dictionary.keys():
            self.centers[cluster_key].move_to(
                self.kmeans.clusters_dictionary[
                    cluster_key].center.point_to_np)
        return [FadeIn(center) for center in self.centers.values()]

    def classify_point(self, point, cluster_key):
        """Set color of point to closest cluster color"""
        return ApplyMethod(point.set_color, self.cluster_color(cluster_key))

    def wiggle_minimum(self, min_line_key):
        """Wiggle the minimum line"""
        return Wiggle(self.ref_lines_group[min_line_key])

    def flash_minimum_distance(self):
        """Flash minimum distance numeric"""
        pass


class Introduction(AssignPoint):
    """Introduce the K-Means"""

    def construct(self):
        self.post_set_up()

        self.introduce_data(self.dots_group, ShowIncreasingSubsets)
        self.wait(3)
        self.play(Write(self.grid))
        self.play(*self.initialize_centers())
        self.wait(3)

        for index, point in enumerate(self.dots_group):
            min_line = self.get_shortest_distance(point)

            self.play(
                self.classify_point(
                    self.dots_group[index],
                    min_line),
                run_time=0.4
            )
            self.wait(0.5)










