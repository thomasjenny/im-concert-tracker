library(shiny)
library(RSQLite)
library(DBI)
library(leaflet)
library(dplyr)
library(DT)
library(purrr)


####################################################################################

# if (grepl("shiny-app", getwd())) {
#   data.raw <- read.csv(file.path(getwd(), "data", "concerts.csv"))
# } else {
#   data.raw <- read.csv(file.path(getwd(), "shiny-app", "data", "concerts.csv"))
# }
# # 
# # 
# # 
# # 
# # Data cleaning - create DF with the information for the text box.
# clean.data <- function(df) {
#  # Define empty DF for all concerts (1 row per concert/setlist)
#  setlists.df <- data.frame(matrix(ncol = 9, nrow = 0))
#  
#  # Loop through all unique concert IDs to create setlists
#  for (concert in unique(df$id)) {
#    single.concert <- subset(df, id == concert)
#      
#      # Add a value to all rows where album_name is NA (i.e., non-original songs) - NOT REQUIRED ANYMORE!
#      # single.concert$album_name[is.na(single.concert$album_name)] <- "Playbacks/Intros/Covers" # %>%
#      
#      # Add a value to all rows where venue is an empty string
#      single.concert$venue[single.concert$venue == ""] <- "Unknown Venue"
#      
#      # Convert empty strings in the cover_info column to NA
#      single.concert <- single.concert %>%
#        mutate(cover = na_if(cover, "")) %>%
#      
#        # Add tape/cover info to the song names in brackets
#        mutate(
#          song_title = case_when(
#            from_tape == 1 & !is.na(cover) ~ paste0(song_title, " (from tape, ", cover, " song)"),
#            from_tape == 1 ~ paste0(song_title, " (from tape)"),
#            !is.na(cover) ~ paste0(song_title, " (", cover, " cover)"),
#            TRUE ~ song_title
#          )
#         ) %>%
# 
#       # Concatenate setlist order numbers and song titles (e.g., 1. The Evil That Men Do)
#       mutate(song_title = ifelse(
#         !is.na(song_count) & !is.na(song_title), paste0(song_count, ". ", song_title), NA
#         )
#       ) %>%
# 
#       # Create a single row for the concert data
#       group_by(id) %>%
#         summarise(
#           date = first(date),
#           venue = first(venue),
#           city = first(city),
#           latitude = first(latitude),
#           longitude = first(longitude),
#           country = first(country),
#           tour = first(tour),
#           song_name = paste(song_title, collapse = "<br>")
#       )
# 
#     # Add the single concert row to the setlists dataframe
#     setlists.df <- rbind(setlists.df, single.concert[1, ])
#    }
# 
#   return(setlists.df)
# }
# 
# im.data.clean <- clean.data(data.raw)
# # write.csv(im.data.clean, "shiny_setlists_data.csv", row.names = FALSE)




####################################################################################



# if (grepl("shiny-app", getwd())) {
#   im.data.clean <- read.csv(file.path(getwd(), "data", "shiny_setlists_data.csv"))
# } else {
#   im.data.clean <- read.csv(file.path(getwd(), "shiny-app", "data", "shiny_setlists_data.csv"))
# }

if (grepl("shiny-app", getwd())) {
  setlists <- read.csv(file.path(getwd(), "data", "app_setlist_data.csv"))
} else {
  setlists <- read.csv(file.path(getwd(), "shiny-app", "data", "app_setlist_data.csv"))
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
    tags$div(
      id = "selection",
        selectInput(
        inputId = "tour",
        label = "Select Tour",
        choices = c("All Tours", unique(im.data.clean$tour))
      )
    ),
    
    # Travel route checkbox
    tags$div(
      id = "selection",
        checkboxInput(
        inputId = "travelroute_checkbox",
        label = "Show Travel Route",
        value = FALSE
      )
    ),
    
    tags$div(id = "travelroute-info", textOutput("travelroute_info")),
    
    # # Test table
    # DTOutput("test.table")
  )
)





####################################################################################
#
# SERVER
#
####################################################################################


server <- function(input, output, session) {
  
  # Create the datasets for visualizations
  
  # Filter the dataset based on the input
  setlist.data <- reactive({
    if (input$tour == "All Tours") {
      # Select everything except the concert_id column
      setlists[, -1]
    } else {
      setlists[setlists$tour == input$tour, -1]
    }
  })
  
  # # Check the test table
  # output$test.table <- renderDT({
  #   datatable(concert.data()[1:20, ], options = list(pageLength = 20))
  # })
  
  # Create data for travel route
  travelroute.data <- reactive({
    setlist.data()[, c("city", "latitude", "longitude")] %>%
      purrr::map_df(rev)
    

    
  })
  
  #########################################################################
  
  
  
  # Create the map
  output$map <- renderLeaflet({
    
    # Define look of the city popups
    popup.output = paste0("<center>",
                            "<font size = 3>",
                              "<b>", setlist.data()$city, ", ", setlist.data()$country, "</b>",
                            "</font>", "<br>",
                            "<font size = 2>",
                              setlist.data()$date, "<br>",
                              setlist.data()$venue,
                            "</font>",
                          "</center>",
                            "<font size = 2>",
                              "<br> <b> Setlist: </b> <br>",
                              # Replace "Encore 1" with "Encore" only
                              sub("Encore 1", "Encore", setlist.data()$setlist),
                            "</font>")
    
    # minZoom = maximal zoom factor possible when zooming out -> prevent app from 
    # showng a small tile with a lot of whitespace around
    map <- leaflet(options = leafletOptions(minZoom = 2.8)) %>%
      # Add the layout for the map
      addProviderTiles(providers$CartoDB.DarkMatter, # Stadia.StamenTonerLite,
                       options = providerTileOptions(noWrap = TRUE)) %>%
      # MaxBounds determine the "end" of the map --> prevent the "ribbon" effect
      setMaxBounds(
        lng1 = -180, lat1 = -75,
        lng2 = 180, lat2 = 83
      ) %>%
      # setView = the starting point / "frame" that you see when you open the app.
      setView(lng = 10, lat = 47, zoom = 4) %>%
      # Add the circle markers
      addCircleMarkers(data = setlist.data(),
                       lng = ~longitude,
                       lat = ~latitude,
                       label = ~city,
                       labelOptions = labelOptions(style = list("font-size" = "12px")),
                       popup = popup.output,
                       # popupOptions = popupOptions(style = list("font-size" = "10px")),
                       color = "#9B2242",
                       stroke = FALSE,
                       radius = 6,
                       fillOpacity = 1)
    
    
    # Display the travel route if an individual tour is selected.
      if (input$travelroute_checkbox == TRUE && input$tour != "All Tours") {
          map <- map %>% addPolylines(data = travelroute.data(),
                     lng = ~longitude,
                     lat = ~latitude,
                     color = "red",
                     weight = 6,
                     opacity = 0.4,
                     smoothFactor = 5)
      }
        
      map
  })
  
  
  # Define text output if "All Tours" is selected from the dropdown and the checkbox
  # is ticked

  
  output$travelroute_info <- renderText({
    if (input$travelroute_checkbox == TRUE && input$tour == "All Tours") {
       "Travel route can only be displayed for a specific tour"
    } else {
       ""
     }
  })
  
  
}


####################################################################################


# Run the application 
shinyApp(ui, server)
