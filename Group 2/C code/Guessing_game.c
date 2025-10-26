#include <gtk/gtk.h>
#include <stdlib.h>
#include <time.h>

typedef struct 
{
    int number;
    int attempts;
    gboolean game_won;
    GtkLabel *status_label;
    GtkEntry *entry;
    GtkRevealer *revealer;
    GtkWidget *status_box;
} GameData;

/* Modern GTK 4 way to show a message dialog */
static void show_popup(GtkWindow *parent, const char *message) 
{
    GtkAlertDialog *dialog = gtk_alert_dialog_new(message);
    gtk_alert_dialog_show(dialog, parent);
    g_object_unref(dialog);
}

/* Modern “animation” using CSS class toggling */
static gboolean reset_color(gpointer data) 
{
    gtk_widget_remove_css_class(GTK_WIDGET(data), "pulse");
    return G_SOURCE_REMOVE;
}

static void animate_feedback(GtkWidget *widget, const char *color) 
{
    GtkCssProvider *provider = gtk_css_provider_new();
    char css[256];
    snprintf(css, sizeof(css),
             ".pulse { background-color: %s; border-radius: 12px; transition: background-color 200ms ease; }",
             color);
    gtk_css_provider_load_from_string(provider, css);
    gtk_style_context_add_provider_for_display(
        gdk_display_get_default(),
        GTK_STYLE_PROVIDER(provider),
        GTK_STYLE_PROVIDER_PRIORITY_USER);
    gtk_widget_add_css_class(widget, "pulse");
    g_timeout_add(300, reset_color, widget);
    g_object_unref(provider);
}

static void on_guess_clicked(GtkButton *button, gpointer user_data) 
{
    GameData *game = (GameData *)user_data;

    // Check if the game has already been won
    if (game->game_won) {
        gtk_label_set_text(game->status_label, "🎉 You already won! Press Reset for a new game.");
        gtk_revealer_set_reveal_child(game->revealer, TRUE);
        return;
    }


    const char *text = gtk_editable_get_text(GTK_EDITABLE(game->entry));
    if (!text || *text == '\0') 
    {
        gtk_label_set_text(game->status_label, "⛔ Enter a number first!");
        gtk_revealer_set_reveal_child(game->revealer, TRUE);
        animate_feedback(GTK_WIDGET(game->status_box), "#FFCDD2");
        return;
    }

    int guess = atoi(text);
    // increase the attempt by 1 
    game->attempts++;   
    GtkWindow *win = GTK_WINDOW(gtk_widget_get_root(GTK_WIDGET(button)));

    //check if the guess is correct
    if (guess == game->number) 
    {
        // Mark the game as won to prevent further guesses#
        game->game_won = TRUE;
        char msg[128];
        snprintf(msg, sizeof(msg), "You got it in %d attempts! 🎯", game->attempts);
        gtk_label_set_text(game->status_label, "🎉 Correct! Well done!");
        gtk_revealer_set_reveal_child(game->revealer, TRUE);
        animate_feedback(GTK_WIDGET(game->status_box), "#C8E6C9");
        show_popup(win, msg);
    } 
    else if (guess < game->number) 
    {
        gtk_label_set_text(game->status_label, "📉 Too low! Try higher!");   // guess is smaller than the number
        gtk_revealer_set_reveal_child(game->revealer, TRUE);
        animate_feedback(GTK_WIDGET(game->status_box), "#FFF59D");
    } 
    else 
    {
        gtk_label_set_text(game->status_label, "📈 Too high! Try lower!");  //guess is greater than the number
        gtk_revealer_set_reveal_child(game->revealer, TRUE);
        animate_feedback(GTK_WIDGET(game->status_box), "#FFECB3");
    }
    
    gtk_editable_set_text(GTK_EDITABLE(game->entry), "");
}

// Callback function executed when the "Reset" button is clicked
static void on_reset_clicked(GtkButton *button, gpointer user_data) 
{
    GameData *game = (GameData *)user_data;
    // generate a random number between 1 and 100 
    game->number = (rand() % 100) + 1;
    game->attempts = 0;
    game->game_won = FALSE; 
    gtk_label_set_text(game->status_label, "🎲 New game started! Guess between 1-100.");
    gtk_revealer_set_reveal_child(game->revealer, TRUE);
    animate_feedback(GTK_WIDGET(game->status_box), "#BBDEFB");
    gtk_editable_set_text(GTK_EDITABLE(game->entry), "");
}

static void app_activate(GtkApplication *app, gpointer user_data) 
{
    GtkWidget *window, *main_box, *entry, *guess_btn, *reset_btn, *status_box;
    GtkWidget *revealer, *status_label, *btn_box;
    GameData *game = g_new0(GameData, 1);

    srand(time(NULL));  //seed the random number generator with the current time 
    game->number = (rand() % 100) + 1;  // generate a random number between 1 and 100 

    // Initialize game state
    game->attempts = 0;
    game->game_won = FALSE;

    window = gtk_application_window_new(app);
    gtk_window_set_title(GTK_WINDOW(window), "🎮 Guess The Number");
    gtk_window_set_default_size(GTK_WINDOW(window), 400, 300);
    gtk_window_set_resizable(GTK_WINDOW(window), FALSE);

    main_box = gtk_box_new(GTK_ORIENTATION_VERTICAL, 12);
    gtk_widget_set_margin_top(main_box, 20);
    gtk_widget_set_margin_bottom(main_box, 20);
    gtk_widget_set_margin_start(main_box, 20);
    gtk_widget_set_margin_end(main_box, 20);
    gtk_window_set_child(GTK_WINDOW(window), main_box);

    GtkWidget *title = gtk_label_new("<big><b>🎯 Guess The Number!</b></big>");
    gtk_label_set_use_markup(GTK_LABEL(title), TRUE);
    gtk_box_append(GTK_BOX(main_box), title);

    entry = gtk_entry_new();
    gtk_entry_set_placeholder_text(GTK_ENTRY(entry), "Type your guess...");
    gtk_widget_add_css_class(entry, "large-entry");
    gtk_box_append(GTK_BOX(main_box), entry);

    btn_box = gtk_box_new(GTK_ORIENTATION_HORIZONTAL, 8);
    gtk_box_append(GTK_BOX(main_box), btn_box);

    guess_btn = gtk_button_new_with_label("✅ Guess");
    gtk_widget_add_css_class(guess_btn, "suggested-action");
    gtk_box_append(GTK_BOX(btn_box), guess_btn);

    reset_btn = gtk_button_new_with_label("🔄 Reset");
    gtk_widget_add_css_class(reset_btn, "destructive-action");
    gtk_box_append(GTK_BOX(btn_box), reset_btn);

    status_box = gtk_frame_new(NULL);
    gtk_box_append(GTK_BOX(main_box), status_box);

    revealer = gtk_revealer_new();
    gtk_revealer_set_transition_type(GTK_REVEALER(revealer), GTK_REVEALER_TRANSITION_TYPE_CROSSFADE);
    gtk_revealer_set_reveal_child(GTK_REVEALER(revealer), TRUE);
    gtk_frame_set_child(GTK_FRAME(status_box), revealer);

    status_label = gtk_label_new("Start guessing a number between 1 and 100!");
    gtk_label_set_wrap(GTK_LABEL(status_label), TRUE);
    gtk_label_set_justify(GTK_LABEL(status_label), GTK_JUSTIFY_CENTER);
    gtk_revealer_set_child(GTK_REVEALER(revealer), status_label);

    game->entry = GTK_ENTRY(entry);
    game->status_label = GTK_LABEL(status_label);
    game->revealer = GTK_REVEALER(revealer);
    game->status_box = status_box;

    g_signal_connect(guess_btn, "clicked", G_CALLBACK(on_guess_clicked), game);
    g_signal_connect(reset_btn, "clicked", G_CALLBACK(on_reset_clicked), game);

    gtk_window_present(GTK_WINDOW(window));
}

int main(int argc, char **argv) 
{
    GtkApplication *app;
    int status;

    app = gtk_application_new("com.example.guessgame", G_APPLICATION_DEFAULT_FLAGS);
    g_signal_connect(app, "activate", G_CALLBACK(app_activate), NULL);
    status = g_application_run(G_APPLICATION(app), argc, argv);
    g_object_unref(app);
    return status;
}
