from sklearn.cluster import DBSCAN
from lib.joing_attention import get_location_gaze

class JointAttentionDBSCAN:
    """Finds clusters of joint attention for multiple people over time.
    TODO: Chris, submit a paper to CSCL 2024 about this.

    Schneider & Pea (2013) follow Richardson & Dale (2005) in defining joint visual 
    attention as when the gazes of a dyad are within a certain distance, within a 
    certain time window. 

    TODO: 
    - Create a sparse distance matrix for the points, which takes into account the 
      distance threshold and time window parameters. The distance is undefined when 
      both points are from the same user. The effect of using such a sparse matrix is
      that a gaze point can only join a cluster when it is within eps of someone else's 
      gaze point. (It is not enough to be close to one's own gaze point at another timestep.)
    - Perform DBSCAN. `min_samples` should be 2. Eps should be set to a constant, 
      determined by how the distance matrix was computed.

    METHOD
    1. Define a gaze point for each player at each moment. Reduce the granularity to make it 
      manageable.
    2. Create a sparse matrix defining pairwise 

    COMPLEXITY
    This algorithm has O(n^2) time complexity. If there are n gaze points and k users, 
    for each of k users, each of that user's (n/k) gaze points is compared with each of 
    the (n - n/k) other gaze points, or n^2 (1 - 1/k). n dominates k. This metric does 
    not respect the triangle inequality, so I doubt scikit-learn's O(n log n) optimizations 
    can be applied. 

    POSSIBLE OPTIMIZATIONS:
    - As suggested in the scikit-learn documentation, "Another way to reduce memory 
      and computation time is to remove (near-)duplicate points and use sample_weight 
      instead."
    - Using a rolling time window, we can greatly speed this up. We don't need to do most
      of the comparisons.
    """

    def __init__(self, distance_threshold=10, window_ms=2):
        self.distance_threshold = distance_threshold
        self.window_ms = window_ms

        def squared_distance(p0, p1):
            """Computes the squared distance between point p0 and p1.
            (Squared distance is used to save the expensive computation of
            a square root. We use a suitable value of eps to compensate.)
            """
            return 

        self.dbscan = DBSCAN(
            eps=TODO,
            min_samples=2,
            metric=distance
        )

    def fit(self, X):
        """
        """
        return self.dbscan.fit(X)

    def compute_sparse_matrix(self, df):
        """
        """

    def close_enough(self, )


    def prepare_df(self, df):
        """Converts a Minecraft analytics dataframe into a series of gaze points 
        with values (u, t, x, y, z) where U is a user ID, t is a timestamp, and 
        (x, y, z) are spatial coordinates.
        """
        user_lookup = {u:i for i, u in enumerate(sorted(df.player.unique()))}
        df['u'] = df.player.apply(lambda u: user_lookup(u))




