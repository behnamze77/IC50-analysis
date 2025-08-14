import numpy as np
import matplotlib
matplotlib.use('Agg')  # برای سازگاری با موبایل
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image
import io
import base64

def logistic_4p(x, a, b, c, d):
    return d + (a - d) / (1 + (x / c) ** b)

def calculate_ic50_with_replicates(concentration_groups, response_groups):
    mean_responses = []
    std_responses = []
    unique_concentrations = []
    
    for conc_group, resp_group in zip(concentration_groups, response_groups):
        unique_conc = np.unique(conc_group)[0]
        unique_concentrations.append(unique_conc)
        mean_responses.append(np.mean(resp_group))
        std_responses.append(np.std(resp_group))
    
    x = np.array(unique_concentrations)
    y = np.array(mean_responses)
    y_err = np.array(std_responses)
    
    initial_guess = [max(y), -1, np.median(x), min(y)]
    params, _ = curve_fit(logistic_4p, x, y, p0=initial_guess, maxfev=10000)
    ic50 = params[2]
    
    plt.figure(figsize=(10, 6))
    plt.errorbar(x, y, yerr=y_err, fmt='o', 
                 label='Experimental data (mean ± SD)',
                 capsize=5, ecolor='red', elinewidth=2)
    
    x_fit = np.logspace(np.log10(min(x)), np.log10(max(x)), 100)
    y_fit = logistic_4p(x_fit, *params)
    plt.plot(x_fit, y_fit, 'b-', label='Fitted curve (4PL)')
    
    plt.xscale('log')
    plt.xlabel('Concentration (μM)')
    plt.ylabel('Response (%)')
    plt.title(f'IC50 = {ic50:.2f} μM')
    plt.legend()
    plt.grid(True)
    
    # ذخیره نمودار در حافظه
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plot_data = base64.b64encode(buf.read()).decode('utf-8')
    plt.close()
    
    return ic50, (unique_concentrations, mean_responses, std_responses), plot_data

class IC50App(App):
    def build(self):
        self.layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # تنظیمات اولیه
        settings_layout = BoxLayout(size_hint_y=None, height=40)
        self.replicate_input = TextInput(hint_text='تعداد تکرارها (مثلاً 3)', multiline=False)
        settings_layout.add_widget(Label(text='تعداد تکرارها:'))
        settings_layout.add_widget(self.replicate_input)
        self.layout.add_widget(settings_layout)
        
        # تعداد غلظت‌ها
        conc_count_layout = BoxLayout(size_hint_y=None, height=40)
        self.conc_count_input = TextInput(hint_text='تعداد غلظت‌ها (مثلاً 5)', multiline=False)
        conc_count_layout.add_widget(Label(text='تعداد غلظت‌ها:'))
        conc_count_layout.add_widget(self.conc_count_input)
        generate_btn = Button(text='ایجاد فرم ورودی')
        generate_btn.bind(on_press=self.generate_input_fields)
        conc_count_layout.add_widget(generate_btn)
        self.layout.add_widget(conc_count_layout)
        
        # بخش ورودی داده‌ها
        self.data_layout = GridLayout(cols=2, spacing=10, size_hint_y=None)
        self.data_layout.bind(minimum_height=self.data_layout.setter('height'))
        
        self.scroll = ScrollView(size_hint=(1, None), size=(400, 300))
        self.scroll.add_widget(self.data_layout)
        self.layout.add_widget(self.scroll)
        
        # دکمه محاسبه
        self.calc_btn = Button(text='محاسبه IC50', size_hint_y=None, height=50, disabled=True)
        self.calc_btn.bind(on_press=self.calculate)
        self.layout.add_widget(self.calc_btn)
        
        return self.layout
    
    def generate_input_fields(self, instance):
        try:
            num_concentrations = int(self.conc_count_input.text)
            if num_concentrations <= 0:
                raise ValueError("تعداد غلظت‌ها باید مثبت باشد")
            
            self.data_layout.clear_widgets()
            
            for i in range(num_concentrations):
                conc_input = TextInput(hint_text=f'غلظت {i+1} (مثلاً 0.01)', multiline=False)
                self.data_layout.add_widget(Label(text=f'غلظت {i+1}:'))
                self.data_layout.add_widget(conc_input)
                
                resp_input = TextInput(hint_text=f'پاسخ‌ها {i+1} (با کاما: 95,98,97)', multiline=False)
                self.data_layout.add_widget(Label(text='پاسخ‌ها:'))
                self.data_layout.add_widget(resp_input)
            
            self.calc_btn.disabled = False
            
        except Exception as e:
            popup = Popup(
                title='خطا',
                content=Label(text=f'خطا در ایجاد فرم: {str(e)}'),
                size_hint=(0.8, 0.4)
            )
            popup.open()
    
    def calculate(self, instance):
        try:
            num_replicates = int(self.replicate_input.text)
            concentration_groups = []
            response_groups = []
            
            num_concentrations = len(self.data_layout.children) // 4
            
            for i in range(num_concentrations):
                conc_widget = self.data_layout.children[4*i + 3]
                resp_widget = self.data_layout.children[4*i + 1]
                
                conc = float(conc_widget.text)
                responses = [float(x.strip()) for x in resp_widget.text.split(',')]
                
                if len(responses) != num_replicates:
                    raise ValueError(f"تعداد پاسخ‌ها برای غلظت {conc} باید {num_replicates} باشد")
                
                concentration_groups.append([conc] * num_replicates)
                response_groups.append(responses)
            
            ic50, stats, plot_data = calculate_ic50_with_replicates(concentration_groups, response_groups)
            
            # ایجاد پاپاپ با نتیجه
            popup_layout = BoxLayout(orientation='vertical')
            
            result_text = f'IC50 = {ic50:.2f} μM\n\n' + \
                         'میانگین‌ها و انحراف معیارها:\n' + \
                         '\n'.join([f'{conc}: {mean:.1f} ± {std:.1f}' 
                                   for conc, mean, std in zip(*stats)])
            
            result_label = Label(text=result_text, size_hint_y=0.4)
            popup_layout.add_widget(result_label)
            
            # نمایش نمودار
            plot_img = Image()
            plot_img.texture = plot_data  # این بخش نیاز به اصلاح داره
            popup_layout.add_widget(plot_img)
            
            popup = Popup(
                title='نتیجه',
                content=popup_layout,
                size_hint=(0.9, 0.9)
            )
            popup.open()
            
        except Exception as e:
            popup = Popup(
                title='خطا',
                content=Label(text=f'خطا: {str(e)}'),
                size_hint=(0.8, 0.4)
            )
            popup.open()

if __name__ == '__main__':
    IC50App().run()
