library(shiny)
library(RSQLite)
library(DBI)
library(leaflet)
library(dplyr)


####

# Get data from DB

conn <- dbConnect(RSQLite::SQLite(), file.path(getwd(), "..", "data", "db", "iron_maiden_concerts.db"))

im.data.raw <- dbGetQuery(conn, "
  SELECT
    concert.concert_id
    ,concert.date
    ,venue.venue
    ,city.city
    ,city.latitude
    ,city.longitude
    ,city.country
    ,concert.tour
    ,setlist.setlist_position
    ,setlist.song_name
    ,album.album_name
    ,setlist.tape
    ,setlist.cover_info
    ,setlist.encore
  FROM concert
  LEFT JOIN venue ON concert.venue_id = venue.venue_id
  LEFT JOIN city ON concert.city_id = city.city_id
  LEFT JOIN setlist ON concert.concert_id = setlist.concert_id
  LEFT JOIN album ON setlist.song_name = album.song_name
  ORDER BY 
    SUBSTR(date, 7, 4) || '-' ||  -- Year
    SUBSTR(date, 4, 2) || '-' ||  -- Month
    SUBSTR(date, 1, 2) DESC       -- Day DESC
    ,setlist_position ASC
;
")
dbDisconnect(conn)

# Clean data
clean.data <- function(df) {
  
  # Define empty DF for all concerts (1 row per concert/setlist)
  setlists.df <- data.frame(matrix(ncol = 10, nrow = 0))
  
  return(setlists.df)
}

im.data.clean <- clean.data(im.data.raw)



####################################################################################
#
# UI
#
####################################################################################

ui <- fluidPage(
  
  # Import Stylesheet
  tags$head(
    tags$link(rel = "stylesheet", type = "text/css", href = "im_app.css")
  ),
  
  # Map element
  leafletOutput("map", width = "100%", height = "100vh")

)





####################################################################################
#
# SERVER
#
####################################################################################


server <- function(input, output, session) {
  
  # Create the map
  output$map <- renderLeaflet({
    # minZoom = maximal zoom factor possible when zooming out -> prevent app from 
    # showng a small tile with a lot of whitespace around
    leaflet(options = leafletOptions(minZoom = 3.1)) %>%
      # Add the layout for the map
      addProviderTiles(providers$CartoDB.DarkMatter, # Stadia.StamenTonerLite,
                       options = providerTileOptions(noWrap = TRUE)) %>%
      # MasBounds determine the "end" of the map --> prevent the "ribbon" effect
      setMaxBounds(
        lng1 = -180, lat1 = -75,
        lng2 = 180, lat2 = 83
      ) %>%
      # setView = the starting point / "frame" that you see when you open the app.
      setView(lng = 10, lat = 47, zoom = 4)
       #%>%
      #addMarkers(data = points())
  })
}


####################################################################################


# Run the application 
shinyApp(ui, server)
