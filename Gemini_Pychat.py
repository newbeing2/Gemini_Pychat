import tkinter as tk
from tkinter import scrolledtext,ttk,messagebox,filedialog
import os
import google.generativeai as ga
import json

class GUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Gemini Pychat")
        self.geometry("800x600")

        self.config_file_path = "./config.json"

        # 配置行和列权重，使 chatbox_frame 可以随窗口调整大小
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # chatbox_frame 父容器内
        chatbox_frame = tk.Frame(self)
        chatbox_frame.grid(row=0, column=0, sticky='nsew')

        self.chatbox = scrolledtext.ScrolledText(
            chatbox_frame,
            wrap=tk.WORD,
            width=55,
            height=28,
            font=("Arial", 12),
            state=tk.DISABLED,
            cursor="xterm",
            borderwidth=2,
            relief=tk.SUNKEN,
            padx=5,
            pady=5
        )
        self.chatbox.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # send_button_frame 父容器内
        send_button_frame = tk.Frame(self)
        send_button_frame.grid(row=1, column=1, sticky='nsew')

        self.send_button = tk.Button(send_button_frame, text="发送",command=self.send_message)
        self.send_button.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.BOTH, expand=True)

        # user_contentbox_frame 父容器内
        user_contentbox_frame = tk.Frame(self)
        user_contentbox_frame.grid(row=1, column=0, sticky='ew')

        self.user_contentbox = tk.Entry(user_contentbox_frame, width=35)
        self.user_contentbox.pack(padx=10, pady=(0, 10), fill=tk.X, expand=True)
        self.user_contentbox.bind('<Return>', lambda event: self.send_message())

        # options_frame 父容器内
        options_frame = tk.Frame(self)
        options_frame.grid(row=0, column=1, sticky='ns')

        # apikey
        apikey_label = tk.Label(options_frame, text="API Key:")
        apikey_label.pack(side=tk.TOP, padx=10, pady=(10, 0))
        self.apikey_box = tk.Entry(options_frame, width=10)
        self.apikey_box.pack(padx=10, pady=10, fill=tk.X, expand=True)

        # 代理，分为协议（http或者socks）、地址（ip地址）和端口
        proxy_label = tk.Label(options_frame, text="代理设置:")
        proxy_label.pack(side=tk.TOP, padx=10, pady=(10, 0))

        proxy_protocol_label = tk.Label(options_frame, text="协议:")
        proxy_protocol_label.pack(side=tk.TOP, anchor='w', padx=20, pady=(0, 0))
        self.proxy_protocol = ttk.Combobox(options_frame, values=["http", "socks"], width=8)
        self.proxy_protocol.current(0)  # 默认选择 http
        self.proxy_protocol.pack(padx=20, pady=(0, 10), fill=tk.X, expand=True)

        proxy_address_label = tk.Label(options_frame, text="地址 (IP):")
        proxy_address_label.pack(side=tk.TOP, anchor='w', padx=20, pady=(0, 0))
        self.proxy_address = tk.Entry(options_frame, width=15)
        self.proxy_address.pack(padx=20, pady=(0, 10), fill=tk.X, expand=True)

        proxy_port_label = tk.Label(options_frame, text="端口:")
        proxy_port_label.pack(side=tk.TOP, anchor='w', padx=20, pady=(0, 0))
        self.proxy_port = tk.Entry(options_frame, width=5)
        self.proxy_port.pack(padx=20, pady=(0, 10), fill=tk.X, expand=True)
        # 模型名称
        model_label = tk.Label(options_frame, text="模型名称:")
        model_label.pack(side=tk.TOP, padx=10, pady=(10, 0))
        self.model_name = tk.Entry(options_frame, width=15)
        self.model_name.pack(padx=10, pady=(0, 10), fill=tk.X, expand=True)
        # 提示词
        prompt_label = tk.Label(options_frame, text="提示词:")
        prompt_label.pack(side=tk.TOP, padx=10, pady=(10, 0))
        self.prompt_entry = tk.Entry(options_frame, width=20)
        self.prompt_entry.pack(padx=10, pady=(0, 10), fill=tk.X, expand=True)
        # 保存配置文件
        self.save_config_button = tk.Button(options_frame, text="保存配置", command=self.save_config)
        self.save_config_button.pack(side=tk.BOTTOM, padx=10, pady=10, fill=tk.X)
        # 导入配置文件
        self.load_config_button = tk.Button(options_frame, text="导入配置", command=self.load_config)
        self.load_config_button.pack(side=tk.BOTTOM, padx=10, pady=10, fill=tk.X)
    def save_config(self):
        config = {
            'apikey': self.apikey_box.get().strip(),
            'proxy_protocol': self.proxy_protocol.get().strip(),
            'proxy_address': self.proxy_address.get().strip(),
            'proxy_port': self.proxy_port.get().strip(),
            'model_name': self.model_name.get().strip(),
            'prompt': self.prompt_entry.get().strip()
        }
        
        try:
            with open(self.config_file_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
            messagebox.showinfo("成功", f"配置已保存至{self.config_file_path}")
        except Exception as e:
            messagebox.showerror("错误", f"保存配置失败: {e}")
    def load_config(self):
        file_path = filedialog.askopenfilename(
            title="选择配置文件",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if not file_path:  
            return
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            required_keys = ['apikey', 'proxy_protocol', 'proxy_address', 
                            'proxy_port', 'model_name', 'prompt']
            
            if not all(key in config for key in required_keys):
                missing_keys = [key for key in required_keys if key not in config]
                messagebox.showerror("错误", f"配置文件缺少必要字段: {', '.join(missing_keys)}")
                return
            
            try:
                port = str(config['proxy_port'])  
                if port != "":  
                    int(port)
            except ValueError:
                messagebox.showerror("错误", "端口必须是数字")
                return
            
            self.apikey_box.delete(0, tk.END)
            self.apikey_box.insert(0, config['apikey'])
            
            if config['proxy_protocol'] in ["http", "socks"]:
                self.proxy_protocol.set(config['proxy_protocol'])
            else:
                self.proxy_protocol.current(0)  # 默认设置为http
                
            self.proxy_address.delete(0, tk.END)
            self.proxy_address.insert(0, config['proxy_address'])
            
            self.proxy_port.delete(0, tk.END)
            self.proxy_port.insert(0, str(config['proxy_port']))
            
            self.model_name.delete(0, tk.END)
            self.model_name.insert(0, config['model_name'])
            
            self.prompt_entry.delete(0, tk.END)
            self.prompt_entry.insert(0, config['prompt'])
            
            messagebox.showinfo("成功", "配置已成功导入")
        
        except json.JSONDecodeError:
            messagebox.showerror("错误", "无效的JSON格式")
        except Exception as e:
            messagebox.showerror("错误", f"导入配置失败: {str(e)}")
    def get_config_info(self):
        config = {
            'apikey': self.apikey_box.get().strip(),
            'proxy_protocol': self.proxy_protocol.get().strip(),
            'proxy_address': self.proxy_address.get().strip(),
            'proxy_port': self.proxy_port.get().strip(),
            'model_name': self.model_name.get().strip(),
            'prompt': self.prompt_entry.get().strip()
        }
        if not config['apikey']:
            messagebox.showerror("错误", "API Key 不能为空")
            return None
        elif not config['model_name']:
            messagebox.showerror("错误","模型名称不能为空")
        try:
            config['proxy_port'] = int(config['proxy_port'])  
        except ValueError:
            messagebox.showerror("错误", "端口必须是数字")
            return None
        
        return config
    
    def send_message(self):  
        config = self.get_config_info()

        if config['proxy_address'] and config['proxy_port']:
            my_http_proxy = f"{config['proxy_protocol']}://{config['proxy_address']}:{config['proxy_port']}"
            os.environ['http_proxy'] = my_http_proxy
            os.environ['https_proxy'] = my_http_proxy
        
        if config is None:
            return
        
        user_input = self.user_contentbox.get().strip()
        self.user_contentbox.delete(0, tk.END)
        if not user_input:
            tk.messagebox.showwarning("警告", "请输入要发送的消息")
            return

        try:
            ga.configure(api_key=config['apikey'])
            choose_model = config['model_name']
            model = ga.GenerativeModel(choose_model)
            prompt = config['prompt'] or "你是一个乐于助人的ai"

            chat = model.start_chat(history=[
                {"role": "user", "parts": prompt},
            ])
            self.append_chat(f"你:{user_input}\n")
            response = chat.send_message(user_input)
            self.append_chat(f"{choose_model}:{response.text}")

            self.append_chat("_" * 63 + "\n")

        except Exception as e:
            messagebox.showerror("错误", f"出现错误: {e}")
    def append_chat(self, message):
        self.chatbox.config(state=tk.NORMAL)
        self.chatbox.insert(tk.END, message)
        self.chatbox.yview(tk.END)  
        self.chatbox.config(state=tk.DISABLED)
def main():
    gui = GUI()
    gui.mainloop()

if __name__ == "__main__":
    main()