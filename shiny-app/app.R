library(shiny)
library(leaflet)
library(dplyr)
library(purrr)
library(cowplot)
library(plotly)


# Get setlists data
setlists <- read.csv(file.path(getwd(), "data", "app_setlist_data.csv"))
# Get data for songs & albums played
albums.songs <- read.csv(file.path(getwd(), "data", "app_albums_songs.csv"))


# ---------------------------------- UI function ----------------------------------
ui <- fluidPage(
  # Import CSS stylesheet
  tags$head(
    tags$link(rel = "stylesheet", type = "text/css", href = "im_app.css")
  ),
  
  # Create the map
  leafletOutput("map", width = "100%", height = "100vh"),
  
  # Create the control panel
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
    
    # Control panel text
    tags$h1("Live Show Database"),
    
    tags$p(
      "This database contains information about all concerts ever played by British 
      heavy metal band Iron Maiden."
    ),
    
    # Tour selection dropdown
    tags$div(
      id = "selection",
      selectInput(
        inputId = "tour",
        label = "Select Tour",
        choices = c("All Tours", unique(setlists$tour))
      )
    ),
    
    # Travel route display checkbox
    tags$div(
      id = "selection",
      checkboxInput(
        inputId = "travelroute_checkbox",
        label = "Show Travel Route",
        value = FALSE
      )
    ),
    
    # Text output if travel rout cannot be displayed
    tags$div(
      id = "travelroute-info",
      textOutput("travelroute_info")
    ),
    
    # Radio buttons to switch between most played albums/songs plot
    tags$div(
      id = "selection",
      radioButtons(
        inputId = "album_song_rb",
        label = "Show statistics for most played...",
        choiceNames = list("Albums", "Songs"),
        choiceValues = list("albums", "songs"),
        inline = TRUE
      )
    ),
    
    # Most played albums/songs plot
    plotlyOutput("albums.plot", width = "100%", height = "300px")
  )
)


# --------------------------------- Server function -------------------------------
server <- function(input, output, session) {
  # Filter both datasets
  # Filter the setlist data based on the tour input
  #
  # Filter the setlist data based on the tour input -> used to display points on the
  # map and populate the popup
  setlist.data <- reactive({
    if (input$tour == "All Tours") {
      setlists[, -1]
    } else {
      setlists[setlists$tour == input$tour, -1]
    }
  })
  
  # Create the travel route data -> select required columns and reverse order
  travelroute.data <- reactive({
    setlist.data()[, c("city", "latitude", "longitude")] %>%
      purrr::map_df(rev)
  })
  
  # Create data for the albums/songs plot
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
    map <- leaflet(options = leafletOptions(minZoom = 2.5)) %>%
      # Add the layout for the map
      addProviderTiles(providers$CartoDB.DarkMatter,
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
        color = "#ec273f",
        stroke = FALSE,
        radius = 7,
        fillOpacity = 1
      )
    
    
    # Display the travel route if an individual tour is selected.
    if (input$travelroute_checkbox == TRUE &&
        input$tour != "All Tours") {
      map <- map %>% addPolylines(
        data = travelroute.data(),
        lng = ~ longitude,
        lat = ~ latitude,
        color = "#ff0000",
        weight = 6,
        opacity = 0.4,
        smoothFactor = 5
      )
    }
    
    map
  })
  
  
  # Define text output if "All Tours" is selected from the dropdown and the travel
  # rout checkbox is ticked -> if yes, display warning
  output$travelroute_info <- renderText({
    if (input$travelroute_checkbox == TRUE &&
        input$tour == "All Tours") {
      "Travel route can only be displayed for a specific tour"
    } else {
      ""
    }
  })
  
  
  # Define most played albums/songs plot
  output$albums.plot <- renderPlotly({
    # Define the text to be displayed on mouseover/hover
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
    
    # Define plot segements colors
    colors <- c(
      "#ec273f",
      "#111111",
      "#a70000",
      "#333333",
      "#602322",
      "#1d1e21",
      "#8d2523",
      "#261415",
      "#ff5252",
      "#372625",
      "#ba332d",
      "#452727",
      "#ba332d",
      "#555555",
      "#ff4537",
      "#777777"
    )
    
    # Donut chart
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
          line = list(color = "#e5e1e6", width = 1)
        ),
        hovertemplate = hover.info
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


# Run the application
shinyApp(ui, server)
