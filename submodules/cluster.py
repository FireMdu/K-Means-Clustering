from numpy import array
import random as rnd
from math import sqrt
import itertools as it
from functools import reduce
from sklearn.datasets import make_blobs


class PointCoord:
    """
    PointCoord object on the 3D coordinate space whose position is
    represented by three values; x, y and z that are of type float
    If the z value is not supplied the PointCoord object lives in a 2D plane
    """

    def __init__(self, x, y, z=0):
        self.x = x
        self.y = y
        self.z = z

    def __repr__(self):
        return "PointCoord({}, {}, {})".format(self.x, self.y, self.z)

    def __add__(self, other):
        return PointCoord(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other):
        return PointCoord(self.x - other.x, self.y - other.y, self.z - other.z)

    def __hash__(self):
        return hash((self.x, self.y, self.z))

    def __eq__(self, other):
        return (self.x, self.y, self.z) == (other.x, other.y, other.z)

    # multiplication where self.__class__ == other.__class__ or other is on
    # the right hand side if self.__class__ != other.__class__
    def __mul__(self, other):
        if isinstance(other, self.__class__):
            return self.x * other.x + self.y * other.y + self.z * other.z
        else:
            return self.x * other, self.y * other, self.z * other

    # multiplication where self.__class__ != other.__class__ and other is on
    # the left hand side
    def __rmul__(self, other):
        return other * self.x, other * self.y , other * self.z

    def distance(self, other) -> float:
        """Return the Euclidean distance between two PointCoord objects"""
        return sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2 + (
                    self.z - other.z) ** 2)

    @property
    def point_to_np(self):
        """Convert point object to numpy array"""
        return array((self.x, self.y, self.z))


class Cluster:
    """
    Cluster object with PointCoord objects making up a cluster. If the z
    value if not defined, the Cluster object is made up of 2D PointCoord
    objects
    """

    def __init__(self, x, y, z=0):
        self.center = PointCoord(x, y, z)
        self.points = []

    def update(self):
        """
        Update Cluster object's center point to be the mean PointCoord
        object formed by getting a sum of all PointCoord objects in the
        cluster and dividing by the total number of PointCoord objects in
        the cluster
        """

        # check length of cluster
        if len(self.points) > 1:
            # get average of all points in self.points list
            average = reduce(lambda x, y: x + y, self.points) * (
                        1 / len(self.points))
        else:
            # if length is 1 get the only point in the list
            average = (self.center.x, self.center.y, self.center.z)
        # update center
        self.center = PointCoord(*average)

    # add PointCoord(x, y, z) object to cluster
    def add_point(self, point: PointCoord):
        """Add point to cluster points"""
        self.points.append(point)


class KMeans:
    def __init__(self, pts: list, k: int):
        self.k = k
        self.points = pts
        self.points_dictionary = self.points_dict()
        self.clusters_dictionary = self.initiate_cluster()

    def points_dict(self) -> dict:
        """
        Dictionary maps point vertices in the geometric space as tuples to
        PointCoord(x, y, z) object
        """
        return {point: PointCoord(*point) for point in self.points}

    @staticmethod
    def iter_point_coord(point) -> PointCoord:
        """Convert iterable point object to PointCoord object"""
        return PointCoord(*point)

    def pick_center_points(self) -> list:
        """
        Return k random points from the points dictionary as the k starting
        centers of each cluster
        """
        return rnd.sample(list(self.points_dictionary.keys()), k=self.k)

    def initiate_cluster(self) -> dict:
        """
        Create a new dictionary of Cluster objects from the picked center
        points
        """
        return {key: Cluster(*val) for key, val in
                enumerate(self.pick_center_points())}

    @staticmethod
    def get_minimum_cluster(dist_dict: dict) -> int:
        """Return the key of the closest Cluster object's centroid """
        return min(dist_dict.keys(), key=(lambda d: dist_dict[d]))

    def reset_cluster_points(self, clusters_dict: dict):
        """
        Reset points for all Cluster objects in the given Cluster objects
        dictionary
        """
        for key, value in clusters_dict.items():
            del value.points[:]
        return self

    def update_clusters(self, clusters_dict: dict):
        """Iterate through all Cluster objects and update centers"""
        for key, value in clusters_dict.items():
            value.update()
        return self

    def iterate_cluster(self, max_iterations) -> iter:
        """Cluster data according to the closest Cluster center"""
        old_data = dict()
        for _ in range(max_iterations):  # max iterations
            for cord, point in self.points_dictionary.items():
                # temp dictionary to store distances(value) between current
                # point and all clusters(keys)
                dist_dictionary = dict()
                # assign points to clusters based on minimum distance to
                # cluster center
                for key, value in self.clusters_dictionary.items():
                    # calculate distance between point and current cluster
                    dist_dictionary[key] = point.distance(value.center)
                # get the key for the closest cluster center
                closest_cluster_key = self.get_minimum_cluster(
                    dist_dictionary)
                # add PointCoord(x, y, z) object to the closest Cluster object
                self.clusters_dictionary[closest_cluster_key].add_point(point)

            # get a dictionary of all current centers(values) of clusters(keys)
            current_data = {key: curr_cluster.center for key, curr_cluster in
                            self.clusters_dictionary.items()}
            # early iteration exit if converged to a cluster
            if old_data == current_data:
                break
            # update old centers data
            old_data = current_data
            # update cluster centers to new values
            self.update_clusters(self.clusters_dictionary)
            yield self.clusters_dictionary
            # reset Cluster object points
            self.reset_cluster_points(self.clusters_dictionary)


class SKLearnKMeans(KMeans):

    def __init__(self, k: int, centers=None, features=2, samples=100,
                 std_dev=1.0):
        """Take in points from sklearn as predefined points for clustering"""

        self.cluster_centers = centers
        self.data_features = features
        self.sample_quantity = samples
        self.data_std_dev = std_dev
        # Generate cluster data from the sklearn library
        self.data_points, self.cluster_keys, self.cluster_centers = make_blobs(
            n_samples=self.sample_quantity, n_features=self.data_features,
            centers=self.cluster_centers, cluster_std=self.data_std_dev,
            return_centers=True
        )

        self.clustered_dict = self.generate_groups(k)
        pts = list(
            map(
                tuple,
                list(it.chain(*self.clustered_dict.values()))
            )
        )
        KMeans.__init__(self, pts, k)

    def generate_groups(self, k) -> dict:
        clusters_dictionary = {cluster_key: [] for cluster_key in range(k)}
        data_information = list(zip(self.data_points, self.cluster_keys))

        def update_dictionary(dictionary, data_info):
            """Update all entries of the clusters dict and return an updated
            dictionary"""
            #
            for point, cluster in data_info:
                cords = point.tolist()
                if self.data_features < 3:
                    cords.extend([0]*(3 - self.data_features))
                # take only the first 3 dimensions
                dictionary[cluster].append(cords[:3])

            return dictionary

        return update_dictionary(clusters_dictionary, data_information)

    def pick_center_points(self) -> list:
        """Return k random points from each cluster data list"""
        return [rnd.choice(el) for el in
                list(it.chain(self.clustered_dict.values()))]


class OptimalSKLearnKMeans(SKLearnKMeans):

    def __init__(self, k, centers=None, features=2, samples=100, std_dev=1.0):
        SKLearnKMeans.__init__(self, k, centers=centers, features=features,
                               samples=samples, std_dev=std_dev)

    def pick_center_points(self):
        """Return k centroids from each cluster data list"""
        return self.cluster_centers


def generate_vertices(n: int, lim: int, three_d=False, seed=100):
    """Return a list of n '(x, y, z)' tuples"""
    rnd.seed(seed)
    if three_d:
        verts = list(
            set(
                [
                    (
                        rnd.triangular(-1.6*lim, 1.6*lim),
                        rnd.triangular(-lim, lim),
                        rnd.triangular(-lim, lim)
                    ) for _ in range(n)
                ]
            )
        )
    else:
        verts = list(
            set(
                [
                    (
                        rnd.triangular(-1.6*lim, 1.6*lim, -3),
                        rnd.triangular(-lim, lim, 2),
                        0
                    ) for _ in range(n)
                ]
            )
        )
    return verts