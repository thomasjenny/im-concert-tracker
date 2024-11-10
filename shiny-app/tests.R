library(dplyr)

# Get number of songs per albums played data
if (grepl("shiny-app", getwd())) {
  albums.songs <- read.csv(file.path(getwd(), "data", "app_albums_songs.csv"))
} else {
  albums.songs <- read.csv(file.path(getwd(), "shiny-app", "data", "app_albums_songs.csv"))
}

# Top N albums (+ songs) data
# input <- "The Future Past"
input <- "Legacy of the Beast"

albums.top.n <- subset(albums.songs, tour == input) %>%
  count(album_name) %>%
  top_n(10) %>%
  arrange(n, album_name)

albums.top.n <- sort_by(albums.top.n, albums.top.n$n, decreasing = TRUE)
names(albums.top.n)[names(albums.top.n) == "album_name"] <- "name"
names(albums.top.n) == "album_name" <- "name"




songs.top.n <- subset(albums.songs, tour == input) %>%
  count(song_title) %>%
  top_n(10) %>%
  arrange(n, song_title)

songs.top.n <- sort_by(songs.top.n, songs.top.n$n, decreasing = TRUE)

# ----------> do the same thing for songs
# ----------> use top_n(xxxxx) to pass a dynamic value to filter for top n


# plot.data <- reactive({
#   
#   # HIER WEGEN TOP N SCHAUEN!!
#   
#   if (input$tour == "All Tours") {
#     data <- im.data.raw[, c("Tour", "Album Name")]
#     data <- subset(data, `Album Name` != "Playbacks/Intros/Covers")
#     data <- data.frame(table(data$`Album Name`)) %>% arrange(-Freq)
#     data <- data %>% slice(1:10)
#   } else {
#     data <- im.data.raw[im.data.raw$Tour == input$tour, c("Tour", "Album Name")]
#     data <- subset(data, `Album Name` != "Playbacks/Intros/Covers")
#     data <- data.frame(table(data$`Album Name`)) %>% arrange(-Freq)
#     data <- data %>% slice(1:10)
#   }
# })