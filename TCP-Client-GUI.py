from kivy.app import App
#kivy.require("1.10.0")
from kivy.lang import Builder
from kivy import utils
from kivy.uix.screenmanager import ScreenManager, Screen
import threading
from TCP_over_UDP import TCP

cur_color = str(utils.get_hex_from_color(utils.get_random_color()))
cur_nick = ""
cur_ip = ""
cur_port = 0
cur_sock = None
recv_lock = threading.Lock()
keep_going = True


class WelcomeScreen(Screen):

    def get_info(self, nick, ip, port):
        global cur_sock, cur_nick, cur_ip, cur_port
        cur_nick = nick.capitalize() + ": "
        cur_ip = ip
        cur_port = int(port)
        try:
            cur_sock = TCP()
            cur_sock.connect((cur_ip, cur_port))
            self.parent.current = "chat_screen"
        except Exception as error:
            print "An error has occured: error is:%s." % error
        

class ChatScreen(Screen):

    def send_message(self, msg):
        cur_sock.send('[b]' + ('[color=%s]' % cur_color) + cur_nick + msg + '[/color]' + '[/b]')
        self.ids.message_input.text = ""
        print '[b]' + ('[color=%s]' % cur_color) + cur_nick + msg + '[/color]' + '[/b]'

    @staticmethod
    def close_connection():
        cur_sock.close()

    def receiving_msg1(self):
        try:
            while True:
                data = cur_sock.recv()
                if data == "Disconnected":
                    print data
                    return
                else:
                    self.ids.chat_scroll_text.text += data + "\n"
        except Exception as error:
            print "an error " + str(error)

    def receiving_msg_handle1(self):
        try:
            t = threading.Thread(target=self.receiving_msg1)
            t.start()
        except Exception as error:
            print "an error" + str(error)

        
class ScreenManagement(ScreenManager):
    pass


presentation = Builder.load_file("main.kv")


class MainsApp(App):
    def build(self):
        return presentation

if __name__ == "__main__":
    MainsApp().run()
