import customtkinter as ctk
from tkinter import messagebox
from tkintermapview import TkinterMapView
import requests
from PIL import Image
from huggingface_hub import InferenceClient
import json
from datetime import datetime

class WeatherAPI:
    API_KEY = "33be9b6d3fd713869bead42941bc3b3f"
    BASE_URL = "https://api.openweathermap.org/data/2.5/weather?"

    def fetch_weather(city):
        url = f"{WeatherAPI.BASE_URL}appid={WeatherAPI.API_KEY}&q={city}"
        response = requests.get(url)
        return response.json() if response.status_code == 200 else None
    
class huggingFaceAPI:
    model_id = "microsoft/Phi-3-mini-4k-instruct"
    API_KEY = "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"
    llm_client = InferenceClient(
        model=model_id,
        timeout=120,
        token=API_KEY
    )
    def call_llm(weather_description: str, prompt: str):
        prompt = f"Based on the following description of todays weather: {weather_description} Please answer the question: {prompt}"
        response = huggingFaceAPI.llm_client.post(
            json={
                "inputs": prompt,
                "parameters": {"max_new_tokens": 200},
                "task": "text-generation",
            },
        )
        generated_text = json.loads(response.decode())[0]["generated_text"]
        print("generated text", generated_text)
        if prompt in generated_text:
            generated_text = generated_text[len(prompt):].strip()
        return generated_text


class WeatherApp:
    def __init__(self, root):
        self.root = root
        self.current_marker = None
        self.openweather_api_key = "33be9b6d3fd713869bead42941bc3b3f"
        self.map_view = None
        self.city_entry = None
        self.weather_textbox = None
        self.current_weather_summary = None

        self.setup_ui()
        self.setup_map()

    def setup_ui(self):
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        self.root.title("Weather Guru")
        self.center_window(700, 400)
        self.create_top_bar()
        self.create_ai_frame()

    def create_top_bar(self):
        top_bar_frame = ctk.CTkFrame(self.root, fg_color="transparent", bg_color="transparent")
        top_bar_frame.place(relx=0.4, rely=0, relwidth=0.6, relheight=0.1)

        self.city_entry = ctk.CTkEntry(top_bar_frame, placeholder_text="Search")
        self.city_entry.pack(side="left", padx=0, pady=5)
        self.city_entry.bind("<Return>", self.on_enter)

        search_image = ctk.CTkImage(Image.open("images/search.png"), size=(15, 15))
        search_button = ctk.CTkButton(master=top_bar_frame, text="", image=search_image, width=15, height=15,
                               border_width=0, corner_radius=0, hover=False, fg_color="transparent",
                               bg_color="transparent", command=self.on_search)
        search_button.pack(side="left", padx=0, pady=5)

        location_icon = ctk.CTkImage(Image.open("images/location.png"), size=(25, 25))
        location_button = ctk.CTkButton(master=top_bar_frame, text="", image=location_icon, width=25, height=25,  
                                        border_width=0, corner_radius=0, hover=False, fg_color="transparent", bg_color="transparent",
                                        command=self.check_current_weather)
        location_button.pack(side="left", padx=75, pady=5)

        self.theme_button = self.create_theme_button(top_bar_frame)

    def create_theme_button(self, parent):
        lit_sun_icon = ctk.CTkImage(Image.open("images/dark.png"), size=(25, 25))
        unlit_sun_icon = ctk.CTkImage(Image.open("images/light.png"), size=(25, 25))

        theme_button = ctk.CTkButton(master=parent, text="",image=lit_sun_icon, width=25, height=25,  
                                        border_width=0, corner_radius=0, hover=False, fg_color="transparent", bg_color="transparent",
                                        command=self.switch_theme)
        theme_button.pack(side="right", padx=5, pady=5)
        theme_button.lit_icon = lit_sun_icon
        theme_button.unlit_icon = unlit_sun_icon
        return theme_button

    def create_ai_frame(self):
        ai_frame = ctk.CTkFrame(self.root, fg_color="transparent", bg_color="transparent")
        ai_frame.place(relx=0.05, rely=0.0, relwidth=0.30, relheight=1)

        self.header_textbox = ctk.CTkTextbox(ai_frame, fg_color="transparent", font=ctk.CTkFont(family="Arial", size=14, weight="bold"),wrap="word")
        self.header_textbox.place(relx=0, rely=0.05, relwidth=1, relheight=0.2)
        self.header_textbox.configure(state="normal")
        self.header_textbox.insert("1.0", "Select a location!")
        self.header_textbox.configure(state="disabled")

        self.weather_textbox = ctk.CTkTextbox(ai_frame, fg_color="transparent", wrap="word")
        self.weather_textbox.place(relx=0, rely=0.25, relwidth=1, relheight=0.40)
        self.weather_textbox.configure(state="normal")
        instruction = "Use the search function or the interactive map to select a location! You will get a real-time weather report from your personal AI assistant - feel free to ask questions about the current weather situation!"
        self.type_text(self.weather_textbox, instruction, 0)
        self.weather_textbox.configure(state="disabled")

        self.question_textbox = ctk.CTkTextbox(ai_frame, fg_color="transparent", wrap="word", border_width=1, border_color="Gray")
        self.question_textbox.place(relx=0, rely=0.8, relwidth=1, relheight=0.15)
        self.question_textbox.configure(state="normal")

        # Add a button to submit the question
        question_button = ctk.CTkButton(master=ai_frame, text="Ask AI", command=self.ask_ai)
        question_button.place(relx=0.7, rely=0.95, relwidth=0.25, relheight=0.05)


    def setup_map(self):
        self.map_view = TkinterMapView(self.root, corner_radius=0)
        self.map_view.place(relx=0.4, rely=1, relwidth=0.6, relheight=0.9, anchor="sw")
        self.map_view.set_position(59.334591, 18.063240)  # Stockholm
        self.map_view.set_zoom(10)

    def center_window(self, width, height):
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

    def on_search(self):
        city = self.city_entry.get()
        self.update_marker(city)

    def on_enter(self, event):
        self.on_search()

    def switch_theme(self):
        if ctk.get_appearance_mode() == "Dark":
            ctk.set_appearance_mode("light")
            ctk.set_default_color_theme("green")
            self.theme_button.configure(image=self.theme_button.lit_icon)
        else:
            ctk.set_appearance_mode("dark")
            ctk.set_default_color_theme("dark-blue")
            self.theme_button.configure(image=self.theme_button.unlit_icon)

    def ask_ai(self):
        question = self.question_textbox.get("1.0", "end").strip()
        print("Question: ", question)
        ai_response = huggingFaceAPI.call_llm(weather_description=self.current_weather_summary, prompt=question)
        self.display_weather(ai_response)
        print("current weather", self.current_weather_summary)

    def check_current_weather(self):
        center_lat, center_lon = self.map_view.get_position()
        print("checking weather for pos", center_lat, center_lon)
        city = self.reverse_geocode(center_lat, center_lon)
        if city:
            self.update_marker(city)

    def update_marker(self, city):
        weather_data = WeatherAPI.fetch_weather(city)
        if weather_data:
            coords = (weather_data["coord"]["lat"], weather_data["coord"]["lon"])
            if self.current_marker is not None:
                self.map_view.delete_all_marker()
            self.current_marker = self.map_view.set_marker(coords[0], coords[1], text=f"{city}")
            self.map_view.set_position(coords[0], coords[1])
            self.map_view.set_zoom(12)

            weather_summary = self.summarize_weather(weather_data)
           
            llm_weather_summary = huggingFaceAPI.call_llm(weather_description=weather_summary, prompt="What is the weather like today?")
            #print("llm response", llm_weather_summary)
            self.update_header_text(city)
            self.display_weather(llm_weather_summary)
            self.current_weather_summary = weather_summary
        else:
            messagebox.showerror("Error", "City not found.")


    def reverse_geocode(self, lat, lon):
        params = {'lat': lat, 'lon': lon, 'format': 'json', 'zoom': 8}
        response = requests.get("https://nominatim.openstreetmap.org/reverse", params=params)
        return response.json().get("name") if response.status_code == 200 else None

    def summarize_weather(self, data):
        description = data["weather"][0]["description"]
        temperature = f"{round(data['main']['temp'] - 273.15, 1)}°C"
        wind = f"{round(data['wind']['speed'], 1)} m/s"
        return f"Today there is a {description} with a temperature of {temperature} and {wind} wind."

    def display_weather(self, summary):
        self.weather_textbox.configure(state="normal")
        self.weather_textbox.delete("1.0", "end")
        self.type_text(self.weather_textbox, summary, 0)
        self.weather_textbox.configure(state="disabled")

    def update_header_text(self, city):
        now = datetime.now()
        header = city + "\n" + str(now.strftime("%A, %B %d, %Y at %I:%M %p"))
        self.header_textbox.configure(state="normal")
        self.header_textbox.delete("1.0", "end")
        self.header_textbox.insert("1.0", header)
        self.weather_textbox.configure(state="disabled")

    def type_text(self, textbox, text, idx):
        if idx < len(text):
            textbox.configure(state="normal")  # Enable the textbox for inserting text
            textbox.insert("end", text[idx])  # Insert the next character
            textbox.configure(state="disabled")  # Disable the textbox again
            self.root.after(25, self.type_text, textbox, text, idx + 1)  # Delay for the typing effect


if __name__ == "__main__":
    root = ctk.CTk()
    app = WeatherApp(root)
    root.mainloop()
