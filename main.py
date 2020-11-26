import matplotlib.pyplot as plt
import geopandas as gpd
import pandas as pd


def natura2000():
    powiaty_file = './warstwy/powiaty.gpkg'

    powiaty_polygon = gpd.read_file(powiaty_file, layer='powiaty').set_crs('EPSG:2180')
    natura_polygon = gpd.read_file(powiaty_file, layer='GDOS:SpecjalneObszaryOchrony').set_crs('EPSG:2180')

    int = gpd.overlay(powiaty_polygon, natura_polygon, how='intersection')

    area_powiaty = gpd.GeoDataFrame(powiaty_polygon.area / 1000000)
    area_int = gpd.GeoDataFrame(int.area / 1000000)
    area_percent = gpd.GeoDataFrame(int.area / powiaty_polygon.area * 100.0)

    powiaty_polygon.insert(2, "Area [km2]", area_powiaty)
    powiaty_polygon.insert(3, "Area Natura [km2]", area_int)
    powiaty_polygon.insert(4, "Area Natura Percent", area_percent)

    for f in range(len(powiaty_polygon["Area [km2]"])):
        if (powiaty_polygon["Area Natura Percent"][f] > 100.0):
            powiaty_polygon["Area Natura Percent"][f] = 100.0

    fig, ax = plt.subplots(1, 1)
    powiaty_polygon.plot(column='Area Natura Percent', ax=ax, legend=True, cmap='RdYlGn_r',
                         legend_kwds={'label': 'Procent Powierzchni obszarów Natura 2000', 'orientation': 'horizontal'})

    headers = ["jpt_nazwa_", "Area [km2]", "Area Natura Percent", "geometry"]
    powiaty_polygon.to_csv('output_area.csv', columns=headers)
    plt.show()


def ludnosc():
    powiaty_file = './warstwy/powiaty.gpkg'
    ludnosc_file = './warstwy/ludnosc1.csv'

    powiaty_polygon = gpd.read_file(powiaty_file, layer='powiaty').set_crs('EPSG:2180')
    ludnosc = pd.read_csv(ludnosc_file, delimiter=";", encoding='utf-8', dtype={'jpt_kod_je': str, 'ludnosc': float})

    powiaty_polygon = powiaty_polygon.merge(ludnosc, on=('jpt_kod_je'))
    ludnosc_tys = gpd.GeoDataFrame(powiaty_polygon['ludnosc'] / 1000)
    powiaty_polygon.insert(2, 'Ludnosc [tys.]', ludnosc_tys)

    fig, ax = plt.subplots(1, 1)
    powiaty_polygon.plot(column='Ludnosc [tys.]', ax=ax, legend=True, cmap='RdYlGn_r',
                         legend_kwds={'label': 'Ludność w powiecie w tysiącach', 'orientation': 'horizontal'})

    headers = ["jpt_nazwa_", "ludnosc"]
    powiaty_polygon.to_csv('output_ludnosc.csv', columns=headers)
    plt.show()

def przystanki():
    nazwa = "Pomorzany"
    przystanki_file = './warstwy/szczecin.gpkg'

    osiedla_polygon = gpd.read_file(przystanki_file, layer='dzielnice_osiedla_szczecin', encoding='utf-8').set_crs('EPSG:2180')
    przystanki_polygon = gpd.read_file(przystanki_file, layer='OT_OIKM_P', encoding='utf-8').set_crs('EPSG:2180')
    budynki_polygon = gpd.read_file(przystanki_file, layer='OT_BUBD_A', encoding='utf-8').set_crs('EPSG:2180')

    przystanki_polygon['geometry'] = przystanki_polygon.buffer(1)

    inter = gpd.overlay(przystanki_polygon, osiedla_polygon.loc[osiedla_polygon['nazwa'] == nazwa], how='intersection')
    osiedle = osiedla_polygon.loc[osiedla_polygon['nazwa'] == nazwa]

    inter['geometry'] = inter.buffer(500)
    inter.insert(2, "pow", 1)

    budynki_polygon.drop(budynki_polygon.loc[budynki_polygon['liczbakond'] > 100].index, inplace=True)
    budynki_polygon.drop(budynki_polygon.loc[~budynki_polygon['x_kod'].isin(['BUBD01', 'BUBD02', 'BUBD03', 'BUBD04'])].index, inplace=True)

    budynki_polygon = gpd.overlay(inter, budynki_polygon, how="intersection")

    area = gpd.GeoDataFrame(budynki_polygon.area)

    budynki_polygon.insert(2, "pow_mieszkalna", 1)
    budynki_polygon.insert(3, "pow_podstawy", area)

    for index, row in budynki_polygon.iterrows():
        budynki_polygon.loc[index, "pow_mieszkalna"] = row["pow_podstawy"] * row["liczbakond"]

    for index, row in inter.iterrows():
        sub_int = gpd.overlay(inter.iloc[[index]], budynki_polygon, how='intersection')
        inter.loc[index, "pow"] = sub_int["pow_mieszkalna"].sum()

    inter.sort_values(by="pow", inplace=True, ascending=False)

    inter_small = inter.head(n=5)
    inter_centroid = inter_small.centroid

    print(inter_small[["nazwa_1", "pow"]])

    fig, ax = plt.subplots(1, 1)
    osiedle.plot(ax=ax, edgecolor = 'k')
    inter_small.plot(column='pow', alpha = 0.5, edgecolor = 'k', legend=True, cmap='RdYlGn_r', ax=ax,
                         legend_kwds={'label': 'Powierzchnia mieszkalna w zasiegu przystanku', 'orientation': 'horizontal'})
    inter_centroid.plot(marker='*', color = 'k', ax=ax)
    plt.show()


def main():
   # natura2000()       # zadanie 1 - w kilku powiatach otrzymałem wynik przekraczający 100% - ustawiam tam wartość 100.0
   # ludnosc()          # zadanie 2
    przystanki()        # zadanie 3 - dość długo się wykonuje, zależnie od wskazanego osiedla w linii 55
    return


if __name__ == '__main__':
    main()
    exit()
