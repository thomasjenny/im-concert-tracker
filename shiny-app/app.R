library(shiny)
library(RSQLite)
library(DBI)
library(leaflet)
library(dplyr)
library(DT)


####################################################################################

# # Get data from DB
# # WD path might change depending on whether the app is run or only the code itself.
# if (grepl("shiny-app", getwd())) {
#   conn <- dbConnect(RSQLite::SQLite(), file.path(getwd(), "..", "data", "db", "iron_maiden_concerts.db"))
# } else {
#   conn <- dbConnect(RSQLite::SQLite(), file.path(getwd(), "data", "db", "iron_maiden_concerts.db"))
# }
# 
# im.data.raw <- dbGetQuery(conn, "
#   SELECT
#     concert.concert_id
#     ,concert.date
#     ,venue.venue
#     ,city.city
#     ,city.latitude
#     ,city.longitude
#     ,city.country
#     ,concert.tour
#     ,setlist.setlist_position
#     ,setlist.song_name
#     ,album.album_name
#     ,setlist.tape
#     ,setlist.cover_info
#     ,setlist.encore
#   FROM concert
#   LEFT JOIN venue ON concert.venue_id = venue.venue_id
#   LEFT JOIN city ON concert.city_id = city.city_id
#   LEFT JOIN setlist ON concert.concert_id = setlist.concert_id
#   LEFT JOIN album ON setlist.song_name = album.song_name
#   ORDER BY 
#     SUBSTR(date, 7, 4) || '-' ||  -- Year
#     SUBSTR(date, 4, 2) || '-' ||  -- Month
#     SUBSTR(date, 1, 2) DESC       -- Day DESC
#     ,setlist_position ASC
# ;
# ")
# dbDisconnect(conn)
# 
# 
# 
# 
# 
# # Data cleaning - create DF with the information for the text box.
# clean.data <- function(df) {
#   # Define empty DF for all concerts (1 row per concert/setlist)
#   setlists.df <- data.frame(matrix(ncol = 9, nrow = 0))
#   
#   # Loop thrugh all unique concert IDs to create setlists
#   for (concert in unique(df$concert_id)) {
#     single.concert <- subset(df, concert_id == concert)
#     
#     # Add a value to all rows where album_name is NA (i.e., non-original songs)
#     single.concert$album_name[is.na(single.concert$album_name)] <- "Playbacks/Intros/Covers" # %>%
#     
#     # Add a value to all rows where venue is an empty string
#     single.concert$venue[single.concert$venue == ""] <- "Unknown Venue"
#     
#     # Convert empty strings in the cover_info column to NA
#     single.concert <- single.concert %>%
#       mutate(cover_info = na_if(cover_info, "")) %>%
#     
#       # Add tape/cover info to the song names in brackets
#       mutate(
#         song_name = case_when(
#           tape == 1 & !is.na(cover_info) ~ paste0(song_name, " (from tape, oringinally by ", cover_info, ")"),
#           tape == 1 ~ paste0 (song_name, " (from tape"),
#           !is.na(cover_info) ~ paste0(song_name, " (", cover_info, " cover)"),
#           TRUE ~ song_name
#         )
#       ) %>%
#       
#       # Concatenate setlist order numbers and song titles (e.g., 1. The Evil That Men Do)
#       mutate(song_name = ifelse(
#         !is.na(setlist_position) & !is.na(song_name), paste0(setlist_position, ". ", song_name), NA
#         )
#       ) %>%
#       
#       # Create a single row for the concert data
#       group_by(concert_id) %>%
#         summarise(
#           date = first(date),
#           venue = first(venue),
#           city = first(city),
#           latitude = first(latitude),
#           longitude = first(longitude),
#           country = first(country),
#           tour = first(tour),
#           song_name = paste(song_name, collapse = "<br>")
#       )
# 
#     # Add the single concert row to the setlists dataframe
#     setlists.df <- rbind(setlists.df, single.concert[1, ])
#   }
#   
#   return(setlists.df)
# }

# im.data.clean <- clean.data(im.data.raw)
# write.csv(im.data.clean, "shiny_setlists_data.csv", row.names = FALSE)




####################################################################################



if (grepl("shiny-app", getwd())) {
  im.data.clean <- read.csv(file.path(getwd(), "data", "shiny_setlists_data.csv"))
} else {
  im.data.clean <- read.csv(file.path(getwd(), "shiny-app", "data", "shiny_setlists_data.csv"))
}

####################################################################################
#
# UI
#
####################################################################################

ui <- fluidPage(
  
  # Import CSS Stylesheet
  tags$head(
    tags$link(rel = "stylesheet", type = "text/css", href = "im_app.css")
  ),
  
  # Map element
  leafletOutput("map", width = "100%", height = "100vh"),
  
  absolutePanel(
    id = "controls",
    class = "panel panel-default",
    fixed = TRUE,
    draggable = FALSE,
    top = 20,
    left = 50,
    right = "auto",
    bottom = "auto",
    width = "30%",
    height = "auto",
    
    # Header image
    tags$img(src = "Iron_Maiden_logo.png", width = "95%"),
    
    # Sidebar Text
    tags$h2("Live Show Database"),
    
    tags$p("This database contains information about all concerts ever played by
           British heavy metal band Iron Maiden."),
    
    # Tour dropdown
    selectInput(
      inputId = "tour",
      label = "Select Tour",
      choices = c("All Tours", unique(im.data.clean$tour))
    ),
    
    # Test table
    DTOutput("test.table")
  )
)





####################################################################################
#
# SERVER
#
####################################################################################


server <- function(input, output, session) {
  
  # Filter the dataset based on the input
  concert.data <- reactive({
    if (input$tour == "All Tours") {
      # Select everything except the concert_id column
      im.data.clean[, -1]
    } else {
      im.data.clean[im.data.clean$tour == input$tour, -1]
    }
  })
  
  # Check the test table
  output$test.table <- renderDT({
    datatable(concert.data()[1:20, ], options = list(pageLength = 20))
  })
  
  
  
  
  # Create the map
  output$map <- renderLeaflet({
    # minZoom = maximal zoom factor possible when zooming out -> prevent app from 
    # showng a small tile with a lot of whitespace around
    leaflet(options = leafletOptions(minZoom = 3.1)) %>%
      # Add the layout for the map
      addProviderTiles(providers$CartoDB.DarkMatter, # Stadia.StamenTonerLite,
                       options = providerTileOptions(noWrap = TRUE)) %>%
      # MaxBounds determine the "end" of the map --> prevent the "ribbon" effect
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
