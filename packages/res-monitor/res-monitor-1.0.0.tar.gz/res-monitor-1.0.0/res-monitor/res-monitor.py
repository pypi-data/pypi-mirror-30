import tkinter as tk
from tkinter import ttk

import psutil


class Application(tk.Frame):
    CPU_USAGE_UPDATE_TIME_MS = 1000

    def __init__(self, master: tk.Tk, proc_info: psutil):
        super().__init__(master)

        self.num_cpus = proc_info.cpu_count()
        self.proc_info = proc_info

        self.quit = tk.Button(self, text="QUIT", fg="red",
                              command=master.destroy)

        self.cpu_labels = []
        self.cpu_bars = []
        self.cpu_names = []
        for i in range(self.num_cpus):
            new_cpu_bar = ttk.Progressbar(self, orient=tk.HORIZONTAL, length=100,
                                          mode='determinate', style="blue.Horizontal.TProgressbar")
            self.cpu_bars.append(new_cpu_bar)

            new_cpu_label = tk.Label(self)
            self.cpu_labels.append(new_cpu_label)

            new_cpu_name = tk.Label(self)
            self.cpu_names.append(new_cpu_name)

        self.pack()
        self.setup_widgets()

    def setup_widgets(self):
        cpu_percent = self.proc_info.cpu_percent(percpu=True)

        for i in range(self.num_cpus):
            self.cpu_bars[i].grid(row=i * 2, columnspan=4)
            self.cpu_labels[i].grid(row=i * 2 + 1, column=2)
            self.cpu_labels[i]['text'] = cpu_percent[i]
            self.cpu_names[i].grid(row=i * 2 + 1, column=0)
            self.cpu_names[i]['text'] = "CPU%d" % i

        self.quit.grid(row=9, column=1)

    def update_cpu_usage(self):
        cpu_percent = self.proc_info.cpu_percent(percpu=True)

        for i in range(self.num_cpus):
            self.cpu_bars[i]['value'] = cpu_percent[i]
            self.cpu_labels[i]['text'] = str(cpu_percent[i])

        self.master.after(self.CPU_USAGE_UPDATE_TIME_MS, self.update_cpu_usage)


if __name__ == '__main__':
    root = tk.Tk()
    app = Application(
        master=root,
        proc_info=psutil
    )

    root.attributes('-type', 'dialog')

    s = ttk.Style()
    s.theme_use('clam')
    s.configure("blue.Horizontal.TProgressbar", foreground='blue', background='blue')

    app.update_cpu_usage()

    app.mainloop()
