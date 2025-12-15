import wx
import wx.grid
import time # Used for simulated payment delay

# --- MOCK DATA (Simulating a Database) ---
MOVIES = [
    {"id": 1, "title": "Avengers: Endgame", "genre": "Action/Sci-Fi", "price": 12.00, "description": "The Avengers take a final stand against Thanos."},
    {"id": 2, "title": "The Lion King", "genre": "Animation/Drama", "price": 10.00, "description": "Simba idolizes his father, King Mufasa, and takes to heart his own royal destiny."},
    {"id": 3, "title": "Inception", "genre": "Sci-Fi/Thriller", "price": 11.50, "description": "A thief who steals corporate secrets through the use of dream-sharing technology."},
    {"id": 4, "title": "Titanic", "genre": "Romance/Drama", "price": 9.00, "description": "A seventeen-year-old aristocrat falls in love with a kind but poor artist."}
]

# Keep track of booked seats per movie ID
BOOKED_SEATS_DB = {
    1: [(0, 2), (0, 3)],
    2: [],
    3: [(2, 2)],
    4: []
}

# --- NEW PAYMENT DIALOG ---

class PaymentDialog(wx.Dialog):
    """ Dialog to collect mock payment information and simulate processing """
    def __init__(self, parent, total_amount):
        super().__init__(parent, title="Complete Payment", size=(400, 350))
        self.total_amount = total_amount
        self.payment_successful = False
        self.init_ui()
        self.Centre()

    def init_ui(self):
        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)
        
        # Header
        lbl_header = wx.StaticText(panel, label=f"Total Due: ${self.total_amount:.2f}")
        lbl_header.SetFont(wx.Font(14, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        vbox.Add(lbl_header, 0, wx.ALL | wx.CENTER, 15)

        # Form Grid
        form_sizer = wx.FlexGridSizer(rows=3, cols=2, vgap=10, hgap=10)
        
        # Card Number
        form_sizer.Add(wx.StaticText(panel, label="Card Number:"), 0, wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT)
        self.txt_card = wx.TextCtrl(panel, value="1234567890123456")
        form_sizer.Add(self.txt_card, 0, wx.EXPAND)
        
        # Expiry Date (Mock)
        form_sizer.Add(wx.StaticText(panel, label="Expiry (MM/YY):"), 0, wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT)
        self.txt_expiry = wx.TextCtrl(panel, value="12/26", size=(60, -1))
        form_sizer.Add(self.txt_expiry, 0)

        # CVV
        form_sizer.Add(wx.StaticText(panel, label="CVV:"), 0, wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT)
        self.txt_cvv = wx.TextCtrl(panel, value="123", size=(50, -1))
        form_sizer.Add(self.txt_cvv, 0)

        vbox.Add(form_sizer, 0, wx.ALL | wx.EXPAND, 20)
        
        # Payment Button
        self.btn_pay = wx.Button(panel, label=f"Pay ${self.total_amount:.2f}")
        self.btn_pay.Bind(wx.EVT_BUTTON, self.on_pay)
        vbox.Add(self.btn_pay, 0, wx.ALL | wx.CENTER, 10)

        # Progress Bar (Simulated processing)
        self.gauge = wx.Gauge(panel, range=100, size=(250, 20))
        vbox.Add(self.gauge, 0, wx.ALL | wx.CENTER, 10)
        
        # Cancel Button
        btn_cancel = wx.Button(panel, wx.ID_CANCEL, "Cancel")
        vbox.Add(btn_cancel, 0, wx.ALL | wx.CENTER, 10)

        panel.SetSizerAndFit(vbox)

    def on_pay(self, event):
        # In a real app, validation and connection to a payment gateway would happen here.
        if len(self.txt_card.GetValue()) < 16 or len(self.txt_cvv.GetValue()) < 3:
            wx.MessageBox("Please enter valid mock card details.", "Validation Error", wx.OK | wx.ICON_ERROR)
            return

        self.btn_pay.Disable()
        self.btn_pay.SetLabel("Processing...")
        
        # Start simulated payment processing
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.on_timer, self.timer)
        self.timer.Start(100) # Tick every 100ms
        self.gauge_value = 0

    def on_timer(self, event):
        self.gauge_value += 5
        self.gauge.SetValue(self.gauge_value)

        if self.gauge_value >= 100:
            self.timer.Stop()
            self.payment_successful = True
            
            # Show success message for 1 second before closing
            self.btn_pay.SetLabel("Payment Successful!")
            self.btn_pay.SetBackgroundColour("GREEN")
            self.btn_pay.SetForegroundColour("WHITE")
            
            wx.CallLater(1000, self.EndModal, wx.ID_OK) # End dialog after 1 second
        elif self.gauge_value == 50:
            # Add a slight delay / visual change for realism
            self.btn_pay.SetLabel("Authorizing...")


# --- EXISTING CLASSES (Modified) ---

class SeatButton(wx.ToggleButton):
    """ Custom Button representing a single seat """
    def __init__(self, parent, id, label, coordinate):
        super().__init__(parent, id, label, size=(40, 40))
        self.coordinate = coordinate # Tuple (row, col)
        self.Bind(wx.EVT_TOGGLEBUTTON, self.on_toggle)
        
    def on_toggle(self, event):
        if self.GetValue():
            self.SetBackgroundColour("GREEN")
        else:
            self.SetBackgroundColour(wx.NullColour)
            
        event.Skip()

class SeatSelectionDialog(wx.Dialog):
    """ The Window where users pick their seats """
    def __init__(self, parent, movie_data):
        super().__init__(parent, title=f"Booking: {movie_data['title']}", size=(500, 600))
        self.movie = movie_data
        self.selected_seats = [] # List of coordinates
        self.ticket_price = movie_data['price']
        
        self.init_ui()
        self.Centre()

    def init_ui(self):
        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)

        # 1. Header Information
        lbl_title = wx.StaticText(panel, label=self.movie['title'])
        lbl_title.SetFont(wx.Font(16, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        
        lbl_price = wx.StaticText(panel, label=f"Price per Ticket: ${self.ticket_price:.2f}")
        
        vbox.Add(lbl_title, 0, wx.ALL | wx.CENTER, 10)
        vbox.Add(lbl_price, 0, wx.ALL | wx.CENTER, 5)
        
        vbox.Add(wx.StaticLine(panel), 0, wx.EXPAND | wx.ALL, 10)

        # 2. The Screen Visual
        screen_box = wx.StaticText(panel, label="--- SCREEN THIS WAY ---", style=wx.ALIGN_CENTER)
        screen_box.SetForegroundColour("GREY")
        vbox.Add(screen_box, 0, wx.ALL | wx.CENTER, 10)

        # 3. Seat Grid (5 rows x 6 columns)
        grid_sizer = wx.GridSizer(rows=5, cols=6, vgap=10, hgap=10)
        
        self.seat_buttons = {}
        already_booked = BOOKED_SEATS_DB.get(self.movie['id'], [])

        rows = "ABCDE"
        for r in range(5):
            for c in range(6):
                seat_label = f"{rows[r]}{c+1}"
                coord = (r, c)
                
                btn = SeatButton(panel, wx.ID_ANY, seat_label, coord)
                
                # Check if seat is already sold in database
                if coord in already_booked:
                    btn.SetBackgroundColour("RED")
                    btn.Disable()
                    btn.SetLabel("X")
                else:
                    btn.Bind(wx.EVT_TOGGLEBUTTON, self.on_seat_click)
                
                grid_sizer.Add(btn, 0)
                self.seat_buttons[coord] = btn

        vbox.Add(grid_sizer, 1, wx.ALIGN_CENTER | wx.ALL, 20)

        # 4. Footer & checkout
        self.lbl_total = wx.StaticText(panel, label="Selected: 0 | Total: $0.00")
        self.lbl_total.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        vbox.Add(self.lbl_total, 0, wx.ALIGN_CENTER | wx.ALL, 10)

        hbox_btns = wx.BoxSizer(wx.HORIZONTAL)
        btn_cancel = wx.Button(panel, wx.ID_CANCEL, "Cancel")
        
        # RENAMED CONFIRM BUTTON TO PROCEED TO PAYMENT
        self.btn_proceed = wx.Button(panel, wx.ID_OK, "Proceed to Payment")
        self.btn_proceed.Disable() 
        self.btn_proceed.Bind(wx.EVT_BUTTON, self.on_proceed_to_payment) # Bound to a new handler

        hbox_btns.Add(btn_cancel, 0, wx.ALL, 5)
        hbox_btns.Add(self.btn_proceed, 0, wx.ALL, 5)
        
        vbox.Add(hbox_btns, 0, wx.ALIGN_CENTER | wx.BOTTOM, 20)

        panel.SetSizer(vbox)

    def on_seat_click(self, event):
        btn = event.GetEventObject()
        coord = btn.coordinate
        
        if btn.GetValue():
            self.selected_seats.append(coord)
        else:
            self.selected_seats.remove(coord)
            
        self.update_totals()

    def update_totals(self):
        count = len(self.selected_seats)
        self.total_amount = count * self.ticket_price
        self.lbl_total.SetLabel(f"Selected: {count} | Total: ${self.total_amount:.2f}")
        
        if count > 0:
            self.btn_proceed.Enable()
        else:
            self.btn_proceed.Disable()

    # --- MODIFIED: Handles Payment Flow ---
    def on_proceed_to_payment(self, event):
        if not self.selected_seats:
            return

        # 1. Open the Payment Dialog
        payment_dlg = PaymentDialog(self, self.total_amount)
        result = payment_dlg.ShowModal()

        # 2. Check if payment was successful
        if result == wx.ID_OK and payment_dlg.payment_successful:
            self.final_book_seats()
        else:
            wx.MessageBox("Payment Cancelled or Failed. Please try again.", "Payment Status", wx.OK | wx.ICON_WARNING)
            
        payment_dlg.Destroy()


    def final_book_seats(self):
        """ This function runs ONLY after payment is confirmed """
        
        # Save to 'database'
        current_booked = BOOKED_SEATS_DB.get(self.movie['id'], [])
        BOOKED_SEATS_DB[self.movie['id']] = current_booked + self.selected_seats
        
        wx.MessageBox(f"Success! Your payment of ${self.total_amount:.2f} was confirmed and you booked {len(self.selected_seats)} tickets.\nEnjoy the show!", 
                      "Booking Confirmed", wx.OK | wx.ICON_INFORMATION)
        
        self.EndModal(wx.ID_OK) # Close main dialog after successful booking


class MoviePanel(wx.Panel):
    """ A visual card for a single movie """
    def __init__(self, parent, movie_data):
        super().__init__(parent, size=(200, 150))
        self.movie_data = movie_data
        
        self.SetBackgroundColour(wx.Colour(240, 240, 240)) # Light grey card
        
        # Layout
        vbox = wx.BoxSizer(wx.VERTICAL)
        
        title = wx.StaticText(self, label=movie_data['title'])
        title.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        
        genre = wx.StaticText(self, label=movie_data['genre'])
        genre.SetForegroundColour("GREY")

        desc = wx.StaticText(self, label=movie_data['description'], style=wx.ALIGN_CENTER)
        desc.Wrap(180) # Wrap text to fit card
        
        btn_book = wx.Button(self, label="Book Now")
        btn_book.Bind(wx.EVT_BUTTON, self.on_book)

        vbox.Add(title, 0, wx.ALIGN_CENTER | wx.TOP, 10)
        vbox.Add(genre, 0, wx.ALIGN_CENTER | wx.BOTTOM, 5)
        vbox.Add(desc, 1, wx.ALIGN_CENTER | wx.ALL, 5)
        vbox.Add(btn_book, 0, wx.ALIGN_CENTER | wx.BOTTOM, 10)
        
        self.SetSizer(vbox)
        
        # Add a simple border
        self.Bind(wx.EVT_PAINT, self.on_paint)

    def on_paint(self, event):
        dc = wx.PaintDC(self)
        dc.SetPen(wx.Pen("BLACK", 1))
        dc.SetBrush(wx.Brush("WHITE", wx.TRANSPARENT))
        w, h = self.GetSize()
        dc.DrawRectangle(0, 0, w, h)

    def on_book(self, event):
        # Open the Seat Selection Dialog
        dlg = SeatSelectionDialog(self.GetTopLevelParent(), self.movie_data)
        # Use ShowModal to wait for the dialog to close
        dlg.ShowModal()
        dlg.Destroy()


class MainFrame(wx.Frame):
    def __init__(self):
        super().__init__(None, title="Python BookMyShow", size=(800, 600))
        self.init_ui()
        self.Centre()

    def init_ui(self):
        panel = wx.Panel(self)
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        # App Header
        header = wx.StaticText(panel, label="Welcome to BookMyShow")
        header.SetFont(wx.Font(18, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        header.SetForegroundColour("RED")
        main_sizer.Add(header, 0, wx.ALL | wx.CENTER, 20)

        # Grid of Movies
        grid = wx.GridSizer(cols=2, hgap=20, vgap=20)
        
        for movie in MOVIES:
            movie_card = MoviePanel(panel, movie)
            grid.Add(movie_card, 0, wx.ALIGN_CENTER)

        main_sizer.Add(grid, 1, wx.ALIGN_CENTER | wx.ALL, 20)
        panel.SetSizer(main_sizer)

if __name__ == "__main__":
    app = wx.App(False)
    frame = MainFrame()
    frame.Show()
    app.MainLoop()