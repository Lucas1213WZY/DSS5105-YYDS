import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from sklearn.cluster import DBSCAN
from scipy.spatial import ConvexHull
from shapely.geometry import Point, Polygon, MultiPolygon
import geopandas as gpd
import numpy as np

class hh_RegionClassifierWithConvexHull:
    def __init__(self, poi_file, eps=0.01, min_samples=3):
        self.poi_data = pd.read_excel(poi_file)
        self.poi_data = self.poi_data.dropna(subset=['region_name'])
        self.eps = eps
        self.min_samples = min_samples
        self.region_hulls = {}
        self.fig, self.axes = plt.subplots(1, 2, figsize=(14, 7))  

        unique_regions = self.poi_data['region_name'].unique()
        colors = list(mcolors.TABLEAU_COLORS.values())
        self.region_colors = {region: colors[i % len(colors)] for i, region in enumerate(unique_regions)}

    def train(self):
        for region in self.poi_data['region_name'].unique():
            region_points = self.poi_data[self.poi_data['region_name'] == region][['latitude', 'longitude']].values
            color = self.region_colors[region]

            dbscan = DBSCAN(eps=self.eps, min_samples=self.min_samples)
            clusters = dbscan.fit_predict(region_points)

            all_points = []
            for cluster in set(clusters):
                if cluster == -1:
                    continue
                cluster_points = region_points[clusters == cluster]
                all_points.extend(cluster_points)

            self.axes[0].scatter(*zip(*region_points), label=f"{region} points", color=color, alpha=0.6)

            if len(all_points) >= 3:
                hull = ConvexHull(all_points)
                hull_points = [all_points[vertex] for vertex in hull.vertices]
                self.region_hulls[region] = Polygon(hull_points)

                hull_path = hull_points + [hull_points[0]]  # closed convex hull
                self.axes[0].plot(*zip(*hull_path), linestyle='-', color=color, linewidth=1.5,
                                  label=f"{region} boundary")
            else:
                self.region_hulls[region] = None

        self.axes[0].set_title("Original POI Points and Convex Hull Boundaries")
        self.axes[0].set_xlabel("Latitude")
        self.axes[0].set_ylabel("Longitude")

    def classify(self, new_data_file):
        new_data = pd.read_excel(new_data_file)
        classified_regions = []

        for _, row in new_data.iterrows():
            point = Point(row['latitude'], row['longitude'])
            region_name = "Unknown"
            for region, polygon in self.region_hulls.items():
                if polygon and polygon.contains(point):
                    region_name = region
                    break
            classified_regions.append(region_name)

        new_data['region_name'] = classified_regions

        for region in new_data['region_name'].unique():
            region_points = new_data[new_data['region_name'] == region][['latitude', 'longitude']].values
            color = self.region_colors.get(region, "gray")  
            self.axes[1].scatter(*zip(*region_points), label=f"{region} new points", color=color, marker='x')

        self.axes[1].set_title("Classified New Data Points")
        self.axes[1].set_xlabel("Latitude")
        self.axes[1].set_ylabel("Longitude")

        plt.suptitle("POI Data and Classified New Data Points", fontsize=16)
        plt.show()

        return new_data

class RegionClassifierWithConvexHull: # Use this for user
    def __init__(self, geojson_file):
        self.region_data = gpd.read_file(geojson_file)
        self.region_hulls = {}

        for _, row in self.region_data.iterrows():
            region_name = row['region_name']
            region_geometry = row['geometry']

            if isinstance(region_geometry, Polygon):
                region_points = list(region_geometry.exterior.coords)
            elif isinstance(region_geometry, MultiPolygon):
                region_points = list(region_geometry.geoms[0].exterior.coords)
            else:
                continue

            region_points = [(point[0], point[1]) for point in region_points]
            if len(region_points) >= 3:
                hull = ConvexHull(region_points)
                hull_points = [region_points[vertex] for vertex in hull.vertices]
                self.region_hulls[region_name] = Polygon(hull_points)
            else:
                self.region_hulls[region_name] = None

    def classify(self, new_point): # Use for classify one point
        point = Point(new_point['latitude'], new_point['longitude'])
        region_name = "Unknown"
        for region, polygon in self.region_hulls.items():
            if polygon and polygon.contains(point):
                region_name = region
                break
        return region_name

    def classify_new_points(self, new_data_file): # Use for classifying points in a file
        new_data = pd.read_excel(new_data_file)
        classified_regions = []

        for _, row in new_data.iterrows():
            region_name = self.classify({'latitude': row['latitude'], 'longitude': row['longitude']})
            classified_regions.append(region_name)

        new_data['region_name'] = classified_regions
        return new_data


class InsideBuilding:
    def __init__(self, total_emission, a=0.6, b=0.25, c=0.15, x=1, y=0.4912, z=0.2632):    # these initial values are from the statistics of sg government
        self.total_emission = total_emission
        self.a = a      # a:percentage of office area 
        self.b = b      # b:percentage of retail area
        self.c = c      # c:percentage of parking area
        self.x = x      # x:ratio of unit emission of office to office in a building
        self.y = y      # y:ratio of unit emission of retail to office in a building
        self.z = z      # z:ratio of unit emission of parking facilities to office in a building

    # for internal usage
    def cal_office_retail_park(self):
        unit_office = self.total_emission / (self.a * self.x + self.b * self.y + self.c * self.z)
        office_emission = self.a * self.x * unit_office
        retail_emission = self.b * self.y * unit_office
        park_emission = self.c * self.z * unit_office
        
        return office_emission, retail_emission, park_emission
    
    # for user input, 需要和total emission 组接洽
    def cal_user_building(self, total_emission=None): # for user to estimate how much emission is expected to have a building
        total_emission = total_emission if total_emission is not None else self.total_emission #???
        
        a = float(input("Enter an area percentage of office (a), if you are not sure, please press Enter") or self.a)
        b = float(input("Enter an area percentage of retail (b), if you are not sure, please press Enter") or self.b)
        c = float(input("Enter an area percentage of parking facilities (c), if you are not sure, please press Enter") or self.c)
        x = float(input("Enter an emission ratio of office (x) usually 1, if you are not sure, please press Enter") or self.x)
        y = float(input("Enter an emission ratio of retail to office (y), if you are not sure, please press Enter") or self.y)
        z = float(input("Enter an emission ratio of parking facilities to office (z), if you are not sure, please press Enter") or self.z)

        building = InsideBuilding(total_emission, a, b, c, x, y, z)
        office_emission, retail_emission, park_emission = building.cal_office_retail_park()

        print(f"office emission: {office_emission}")
        print(f"retail emission: {retail_emission}")
        print(f"parking facilities emission: {park_emission}")

def geospatial_vis(geojson_data, type=None):
    if type is None or type=='Total':
        vis_geo_total = geojson_data[['region_name', 'total_trans', 'geometry']]
        cmap = plt.get_cmap('YlOrRd')  
        new_cmap = mcolors.LinearSegmentedColormap.from_list('custom_cmap', ['white', *cmap(np.linspace(0.2, 1, 100))])

        fig, ax = plt.subplots(1, 1, figsize=(12, 6))
        vis_geo_total.plot(column='total_trans', 
                        cmap=new_cmap,         
                        linewidth=0.8, 
                        ax=ax, 
                        legend=True,          
                        edgecolor="black", 
                        vmin=0,               
                        vmax=vis_geo_total['total_trans'].quantile(0.9) 
                        )
        for _, row in vis_geo_total.iterrows():
            centroid = row['geometry'].centroid
            ax.text(centroid.x, centroid.y, row['region_name'], fontsize=5, ha='center', color='black')
        ax.set_title("Heatmap of Total Transportation by Region", fontsize=15)
        ax.set_axis_off()
        plt.show()
    
    if type is None or type=='Transportation':
        vis_geo_mrt_bus_pv = geojson_data[['region_name', 'trans_mrt', 'trans_bus', 'trans_pv', 'geometry', 'total_trans']]
        cmap = plt.get_cmap('YlOrRd')  
        new_cmap = mcolors.LinearSegmentedColormap.from_list('custom_cmap', ['white', *cmap(np.linspace(0.2, 1, 100))])
        norm = mcolors.Normalize(vmin=0, vmax=vis_geo_mrt_bus_pv['total_trans'].quantile(0.9))
        fig, axes = plt.subplots(1, 3, figsize=(12, 6))
        
        #subplot of MRT
        vis_geo_mrt_bus_pv.plot(column='trans_mrt', 
                                cmap=new_cmap,
                                linewidth=0.8, 
                                ax=axes[0], 
                                legend=False,
                                edgecolor="black", 
                                norm=norm)
        axes[0].set_title("Heatmap of MRT Contribution by Region", fontsize=7)
        axes[0].set_axis_off()

        # subplot of bus
        vis_geo_mrt_bus_pv.plot(column='trans_bus', 
                                cmap=new_cmap,
                                linewidth=0.8, 
                                ax=axes[1], 
                                legend=False,
                                edgecolor="black", 
                                norm=norm)
        axes[1].set_title("Heatmap of Bus Contribution by Region", fontsize=7)
        axes[1].set_axis_off()

        # subplot of private vehicles
        vis_geo_mrt_bus_pv.plot(column='trans_pv', 
                                cmap=new_cmap,
                                linewidth=0.8, 
                                ax=axes[2], 
                                legend=False,
                                edgecolor="black", 
                                norm=norm)
        axes[2].set_title("Heatmap of Private Vehicle Contribution by Region", fontsize=7)
        axes[2].set_axis_off()

        plt.tight_layout()
        plt.show()
    

if __name__ == "__main__":
    gep = gpd.read_file('../data/MasterPlan2019.geojson')
    classifier = RegionClassifierWithConvexHull('../data/MasterPlan2019.geojson')
    point = {'longitude':1.307183467, 'latitude':103.7901915}
    region = classifier.classify(point)
    print(region)

