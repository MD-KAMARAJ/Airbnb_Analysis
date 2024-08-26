import pandas as pd
import streamlit as st
import plotly.express as px
import folium
from folium.plugins import MarkerCluster
from streamlit_option_menu import option_menu
import streamlit.components.v1 as components
import plotly.graph_objs as go

st.set_page_config(layout="wide")

col1,col2 = st.columns([1,2])

col1.image(image="airbnb_logo.png",width=100)

col2.title(":red[Airbnb Analysis]")

selected = option_menu( 
    menu_title=None,
    options= ["Home","Analysis"],
    icons=["Home","gear"],
    orientation='horizontal'
)

airbnb_data=pd.read_csv("C:\\Users\\HP USER\\Documents\\Guvi\\Project\\03_Airbnb\\Github\\airbnb_without_outlier_treatment.csv")
df = pd.DataFrame(airbnb_data)
df['Count of ID'] = df.groupby('address.country')['_id'].transform('nunique')

def get_rating_range_options():
        return {
            "0-10": range(0, 11),
            "11-20": range(11, 21),
            "21-30": range(21, 31),
            "31-40": range(31, 41),
            "41-50": range(41, 51),
            "51-60": range(51, 61),
            "61-70": range(61, 71),
            "71-80": range(71, 81),
            "81-90": range(81, 91),
            "91-100": range(91, 101),
    }

if selected == "Home":
    # Create tabs within the Home section
    col1, col2 = st.columns([5,5])
    #(['**🛈 ABOUT**', '**🗺️ Locations**'])

    with col1:
        st.subheader("About Airbnb:")
        st.write('''Airbnb is an online marketplace that connects people looking to rent out their homes with those seeking accommodations. 
        Founded in 2008 by Brian Chesky, Joe Gebbia, and Nathan Blecharczyk, the platform allows hosts to list their properties—ranging from single rooms to entire homes—on the Airbnb website or app,
        where guests can book short-term stays.''')
        st.subheader('Key Features')
        st.subheader('Diverse Listings:') 
        st.markdown('Airbnb offers a wide variety of accommodation options, including apartments, houses, villas, castles, treehouses, and even boats.')
        st.subheader('Global Reach:')
        st.write('With millions of listings in over 220 countries and regions, Airbnb provides a global platform for both hosts and travelers.')
        st.subheader('Experiences and Adventures:')
        st.write('In addition to accommodations, Airbnb offers "Experiences" which are activities hosted by local experts, and "Adventures," which are multi-day guided trips.')
        st.subheader('Host and Guest Reviews:')
        st.write('Both hosts and guests can leave reviews for each other, creating a community-based trust system.')
        st.subheader('Flexible Booking Options:')
        st.write('Airbnb offers flexible cancellation policies and various payment options, making it convenient for users to book stays.')
    
    with col2:

        st.subheader("Locations")
        m = folium.Map(location=[df["latitude"].mean(), df["longitude"].mean()],
                        zoom_start=2,
                        tiles='https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
                        attr='Map data © <a href="https://openstreetmap.org">OpenStreetMap</a> contributors')

            # Add markers for each country
        marker_cluster = MarkerCluster().add_to(m)
        for i, row in df.iterrows():
            folium.Marker(
                location=[row['latitude'], row['longitude']],
                popup=f"{row['address.country']}<br>Count of ID: {row['Count of ID']}",
                icon=folium.Icon(color='red')
               ).add_to(marker_cluster)

            # Save the map as an HTML file
        m.save("map.html")

            # Display the map in Streamlit
        st.components.v1.html(open("map.html", "r").read(), height=600)

    
elif selected == 'Analysis':
    tab3,tab4,tab5,tab6=st.tabs(['Price', 'Location', 'Availability','Drildown'])
    with tab3:
        countries=df['address.country'].unique()
        selected_country=tab3.selectbox("Select Country", [countries[0],countries[1],countries[2],countries[3],countries[4],countries[5],countries[6],countries[7],countries[8]])
        min_price = df["price"].min()
        max_price = df["price"].max()
        
        
    # Create a slider for selecting the price range
        price_range = tab3.slider("Select a price range:",min_price,max_price,(min_price, max_price))
        price_analyser_df=df[['_id','address.country','property_type','room_type','accommodates','review_scores.review_scores_rating','amenities','price']]
        rating_range_options = get_rating_range_options()
        selected_ranges = []
        tab3.markdown("Select your ratings:")
        for labels, range_values in rating_range_options.items():
            if tab3.checkbox(labels):
                selected_ranges.extend(range_values)
        Price_df=price_analyser_df[(price_analyser_df['address.country'] == selected_country) & (price_analyser_df['price'] >= price_range[0]) & (price_analyser_df['price'] <= price_range[1]) & 
                                   (price_analyser_df['review_scores.review_scores_rating'].isin(selected_ranges))]
        st.table(Price_df)

    with tab4:
        properties=df['property_type'].unique()
        properties_1=list(properties)
        select_property=tab4.selectbox("Select Property_type", properties_1)
        countries=df['address.country'].unique()
        countries_1=list(countries)
        rooms=df['room_type'].unique()
        rooms_1=list(rooms)
        filtered_df = df[(df['property_type'] == select_property)]
        
        pie_fig = px.sunburst(
            filtered_df,
            path=['address.country', 'room_type'],
            values='price',
            color='address.country',
            hover_data='price',
            title=f"Price of {select_property} in various countries")
        pie_fig.update_layout(width=1000, height=800)
        tab4.plotly_chart(pie_fig)
    
        col4,col5 = tab4.columns([4,5])

        with col4:
            select_country=col4.selectbox("Choose your country", countries_1)
            filtered_df_country = df[(df['address.country'] == select_country)]

        scatter_fig = px.scatter(
                filtered_df_country,
                x='property_type',
                y='price',
                color='room_type',
                size_max= 500,   
                title="scatter plot showing room types in each properties and in each country")
        scatter_fig.update_layout(width=900, height=600)
        col4.plotly_chart(scatter_fig)

        with col5:
            if 'latitude' in filtered_df_country.columns and 'longitude' in filtered_df_country.columns:
                map_fig = px.scatter_mapbox(
                    filtered_df_country,
                    lat='latitude',
                    lon='longitude',
                    color='property_type',
                    size='price',  # Optional: Size by price, can be omitted if not needed
                    #hover_name='property_type',  # Optional: Add more details on hover
                    title="Map showing locations of selected property type in selected country",
                    zoom=8,  # Adjust zoom level
                    height=300  # Adjust height
                )

            # Update map layout
                map_fig.update_layout(
                    mapbox_style="open-street-map",
                    width=800,  # Adjust width
                    height=600,  # Adjust height
                    margin={"r":0,"t":0,"l":0,"b":0}  # Remove margins for better fit
                )

                col5.plotly_chart(map_fig)
            else:
                col5.write("Latitude and Longitude columns are missing in the DataFrame.")

    with tab5:
        select_country=tab5.selectbox("choose your country", countries_1)
        availability_df_country = df[(df['address.country'] == select_country)]

        col6,col7=tab5.columns([6,7])
        with col6:
            scatter_fig_30 = px.scatter(
                    availability_df_country,
                    x='property_type',
                    y='availability.availability_30',
                    color='room_type',
                    size_max= 6000,   
                    title="scatter plot showing room types in each properties and in each country")
            scatter_fig_30.update_layout(width=1000, height=800)
            col6.plotly_chart(scatter_fig_30)
        with col7:
            scatter_fig_60 = px.scatter(
                    availability_df_country,
                    x='property_type',
                    y='availability.availability_60',
                    color='room_type',
                    size_max= 6000,   
                    title="scatter plot showing room types in each properties and in each country")
            scatter_fig_60.update_layout(width=1000, height=800)
            col7.plotly_chart(scatter_fig_60)

        col8,col9=tab5.columns([8,9])
        with col8:
            scatter_fig_90 = px.scatter(
                    availability_df_country,
                    x='property_type',
                    y='availability.availability_90',
                    color='room_type',
                    size_max= 6000,   
                    title="scatter plot showing room types in each properties and in each country")
            scatter_fig_90.update_layout(width=1000, height=800)
            col8.plotly_chart(scatter_fig_90)
        with col9:
            scatter_fig_365 = px.scatter(
                    availability_df_country,
                    x='property_type',
                    y='availability.availability_365',
                    color='room_type',
                    size_max= 6000,   
                    title="scatter plot showing room types in each properties and in each country")
            scatter_fig_365.update_layout(width=1000, height=800)
            col9.plotly_chart(scatter_fig_365)

    with tab6:
        select_country_dd=tab6.selectbox("Choose country", countries_1)
        select_property_dd=tab6.selectbox("Select Property type", properties_1)
        select_room_dd=tab6.selectbox("Select room type", rooms_1)

        neighbourhood_df=df[['host.host_neighbourhood', 'address.country', 'property_type', 'room_type']]
        neighbourhood_country_df = neighbourhood_df[(neighbourhood_df['address.country'] == select_country_dd) & (neighbourhood_df['property_type'] == select_property_dd) & (neighbourhood_df['room_type'] == select_room_dd)]
        neighbourhood_1 = neighbourhood_country_df['host.host_neighbourhood'].unique()
    
        select_neighbourhood_dd = tab6.selectbox("Select neighbourhood", neighbourhood_1)
    
        Drilldown_df=df[['_id','address.country','property_type','room_type','host.host_neighbourhood','accommodates','review_scores.review_scores_rating','amenities','price']]
        Drilldown_df_1=Drilldown_df[(Drilldown_df['address.country'] == select_country_dd) & (Drilldown_df['property_type'] == select_property_dd) & 
                                    (Drilldown_df['room_type'] == select_room_dd) & (Drilldown_df['host.host_neighbourhood'] == select_neighbourhood_dd)]
        tab6.table(Drilldown_df_1)    