library(shiny)
library(leaflet)
library(dplyr)
# library(DT)
library(purrr)
library(cowplot)
library(plotly)


# Only relevant if local data should be used
# # Get setlists data
# if (grepl("shiny-app", getwd())) {
#   setlists <- read.csv(file.path(getwd(), "data", "app_setlist_data.csv"))
# } else {
#   setlists <- read.csv(file.path(getwd(), "shiny-app", "data", "app_setlist_data.csv"))
# }
# 
# # Get data for songs & albums played
# if (grepl("shiny-app", getwd())) {
#   albums.songs <- read.csv(file.path(getwd(), "data", "app_albums_songs.csv"))
# } else {
#   albums.songs <- read.csv(file.path(getwd(), "shiny-app", "data", "app_albums_songs.csv"))
# }

# Get setlists data
setlists <- read.csv(file.path(getwd(), "data", "app_setlist_data.csv"))
# Get data for songs & albums played
albums.songs <- read.csv(file.path(getwd(), "data", "app_albums_songs.csv"))


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
    
    tags$p(
      "This database contains information about all concerts ever played by
           British heavy metal band Iron Maiden."
    ),
    
    # Tour dropdown
    tags$div(
      id = "selection",
      selectInput(
        inputId = "tour",
        label = "Select Tour",
        choices = c("All Tours", unique(setlists$tour))
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
    
    
    radioButtons(
      inputId = "album_song_rb",
      label = "Show statistics for most played...",
      choiceNames = list("Albums", "Songs"),
      choiceValues = list("albums", "songs"),
      inline = TRUE
    ),
    
    
    
    plotlyOutput("albums.plot", width = "100%", height = "300px")
  )
)





####################################################################################
#
# SERVER
#
####################################################################################


server <- function(input, output, session) {
  # Define input
  
  
  # Filter the dataset based on the input
  setlist.data <- reactive({
    if (input$tour == "All Tours") {
      # Select everything except the concert_id column
      setlists[, -1]
    } else {
      setlists[setlists$tour == input$tour, -1]
    }
  })
  
  
  
  # Create data for travel route
  travelroute.data <- reactive({
    setlist.data()[, c("city", "latitude", "longitude")] %>%
      purrr::map_df(rev)
  })
  
  
  # Create data for albums data
  albums.data <- reactive({
    if (input$tour == "All Tours") {
      albums.top.n <- albums.songs %>%
        count(album_name) %>%
        top_n(10) %>%
        arrange(n, album_name)
      
      albums.top.n <- sort_by(albums.top.n, albums.top.n$n, decreasing = TRUE)
      names(albums.top.n)[names(albums.top.n) == "album_name"] <- "name"
    } else {
      albums.top.n <- subset(albums.songs, tour == input$tour) %>%
        count(album_name) %>%
        top_n(10) %>%
        arrange(n, album_name)
      
      albums.top.n <- sort_by(albums.top.n, albums.top.n$n, decreasing = TRUE)
      names(albums.top.n)[names(albums.top.n) == "album_name"] <- "name"
    }
    
    albums.top.n
  })
  
  
  
  # Create data for songs data
  songs.data <- reactive({
    if (input$tour == "All Tours") {
      songs.top.n <- albums.songs %>%
        count(song_title) %>%
        top_n(10) %>%
        arrange(n, song_title)
      
      songs.top.n <- sort_by(songs.top.n, songs.top.n$n, decreasing = TRUE)
      names(songs.top.n)[names(songs.top.n) == "song_title"] <- "name"
    } else {
      songs.top.n <- subset(albums.songs, tour == input$tour) %>%
        count(song_title) %>%
        top_n(10) %>%
        arrange(n, song_title)
      
      songs.top.n <- sort_by(songs.top.n, songs.top.n$n, decreasing = TRUE)
      names(songs.top.n)[names(songs.top.n) == "song_title"] <- "name"
    }
    
    songs.top.n
  })
  
  
  #########################################################################
  
  
  
  # Create the map
  output$map <- renderLeaflet({
    data <- setlist.data()
    
    if (input$tour == "All Tours") {
      data <- data %>%
        group_by(city, country, latitude, longitude) %>%
        mutate(concert_list = paste(paste0(date, ": ", tour), collapse = "<br>")) %>%
        ungroup() %>%
        distinct(city, country, latitude, longitude, concert_list) %>%
        mutate(
          popup.text = paste0(
            "<center>",
            "<font size = 2>",
            "All concerts played in",
            "</font>",
            "<br>",
            "<font size = 3>",
            "<b>",
            city,
            ", ",
            country,
            "</b>",
            "</font>",
            "</center>",
            "<div class='custom-popup'>",
            "<br>",
            "<font size = 2>",
            concert_list,
            "</font>"
          )
        )
    } else {
      data <- data %>%
        group_by(city, country, latitude, longitude) %>%
        summarise(concert_details = paste(
          paste0(
            "<center>",
            date,
            "<br>",
            venue,
            "</center>",
            "<br><b>Setlist:</b><br>",
            sub("Encore 1", "Encore", setlist)
          ),
          collapse = "<br><br>"
        )) %>%
        ungroup() %>%
        mutate(
          popup.text = paste0(
            "<center>",
            "<font size = 3>",
            "<b>",
            city,
            ", ",
            country,
            "</b>",
            "</font>",
            "<br>",
            "</center>",
            "<div class='custom-popup'>",
            "<font size = 2>",
            concert_details,
            "</font>"
          )
        )
    }
    
    
    # minZoom = maximal zoom factor possible when zooming out -> prevent app from
    # showng a small tile with a lot of whitespace around
    map <- leaflet(options = leafletOptions(minZoom = 2.8)) %>%
      # Add the layout for the map
      addProviderTiles(providers$CartoDB.DarkMatter, # Stadia.StamenTonerLite,
                       options = providerTileOptions(noWrap = TRUE)) %>%
      # MaxBounds determine the "end" of the map --> prevent the "ribbon" effect
      setMaxBounds(
        lng1 = -180,
        lat1 = -75,
        lng2 = 180,
        lat2 = 83
      ) %>%
      # setView = the starting point / "frame" that you see when you open the app.
      setView(lng = 10,
              lat = 47,
              zoom = 4) %>%
      # Add the circle markers
      addCircleMarkers(
        data = data,
        lng = ~ longitude,
        lat = ~ latitude,
        label = ~ city,
        labelOptions = labelOptions(style = list("font-size" = "12px")),
        popup = ~ popup.text,
        # popupOptions = popupOptions(style = list("font-size" = "10px")),
        color = "#9B2242",
        stroke = FALSE,
        radius = 6,
        fillOpacity = 1
      )
    
    
    
    
    # Display the travel route if an individual tour is selected.
    if (input$travelroute_checkbox == TRUE &&
        input$tour != "All Tours") {
      map <- map %>% addPolylines(
        data = travelroute.data(),
        lng = ~ longitude,
        lat = ~ latitude,
        color = "red",
        weight = 6,
        opacity = 0.4,
        smoothFactor = 5
      )
    }
    
    map
  })
  
  
  # Define text output if "All Tours" is selected from the dropdown and the checkbox
  # is ticked
  
  
  output$travelroute_info <- renderText({
    if (input$travelroute_checkbox == TRUE &&
        input$tour == "All Tours") {
      "Travel route can only be displayed for a specific tour"
    } else {
      ""
    }
  })
  
  
  
  
  
  
  # Define Donut Chart
  output$albums.plot <- renderPlotly({
    if (input$album_song_rb == "albums") {
      plot.data <- albums.data
      hover.info <- paste(
        "Total number of songs played from <br>",
        "<i>%{label}</i>: <br>",
        "%{value} (%{percent})<extra></extra>"
      )
    } else {
      plot.data <- songs.data
      hover.info <- paste(
        "Total number of plays of <br>",
        "<i>%{label}: <br>",
        "%{value} (%{percent})<extra></extra>"
      )
    }
    
    # Definition of colors for plot segments (start with red)
    # colors <- c("#9B2242", "#D9D9D6", "#EB212E", "#726E75", "#F4364C",
    #             "#8A8D8F", "#A1000E", "#E5E1E6", "#D22730", "#63666A")
    
    colors <- c(
      "#060607",
      "#1d1e21",
      "#261415",
      "#372625",
      "#452727",
      "#602322",
      "#8d2523",
      "#ba332d",
      "#ff4537",
      "#ff8e6d",
      "#f1a39d",
      "#ffcbb5"
    )
    
    # Donut chart
    # albums.data() %>%
    plot.data() %>%
      plot_ly() %>%
      
      add_trace(
        type = "pie",
        hole = 0.5,
        labels = ~ name,
        values = ~ n,
        textinfo = "label",
        automargin = TRUE,
        textposition = "outside",
        outsidetextfont = list(color = "#e5e1e6"),
        marker = list(
          colors = colors,
          line = list(color = "#ffffff", width = 1)
        ),
        hovertemplate = hover.info
        # hovertemplate = paste("Total number of songs played from <br>",
        #                      "<i>%{label}</i>: <br>",
        #                        "%{value} (%{percent})<extra></extra>")
      ) %>%
      layout(
        showlegend = FALSE,
        paper_bgcolor = "#1f2022",
        xaxis = list(
          showgrid = FALSE,
          zeroline = FALSE,
          showticklabels = FALSE
        ),
        yaxis = list(
          showgrid = FALSE,
          zeroline = FALSE,
          showticklabels = FALSE
        )
      ) %>%
      config(displayModeBar = FALSE)
  })
  
  
  
  
  
  
}


####################################################################################


# Run the application
shinyApp(ui, server)
