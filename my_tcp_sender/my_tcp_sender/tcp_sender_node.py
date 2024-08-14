import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
import socket

class VelocityTcpSenderNode(Node):
    def __init__(self):
        super().__init__('velocity_tcp_sender_node')

        # Configuration du client TCP
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_ip = '10.89.2.196'  # IP du FiPy
        self.server_port = 1234
        
        # Connexion au serveur
        self.connect_to_server()

        # Abonnement au topic de vitesse
        self.subscription = self.create_subscription(
            Twist,
            '/turtle1/cmd_vel',  # Topic du simulateur ou du robot
            self.listener_callback,
            10
        )

        # Création d'un timer pour vérifier régulièrement
        self.create_timer(5.0, self.check_connection)  # Vérifie toutes les 5 secondes

    def connect_to_server(self):
        try:
            self.client_socket.connect((self.server_ip, self.server_port))
            self.get_logger().info(f'Connecté au serveur TCP {self.server_ip}:{self.server_port}')
        except Exception as e:
            self.get_logger().error(f'Échec de la connexion au serveur TCP: {e}')

    def listener_callback(self, msg):
        # Extraction des vitesses linéaires et angulaires
        linear_velocity = msg.linear.x
        angular_velocity = msg.angular.z

        # Formatage du message
        message = f'Velocity: {linear_velocity:.2f} m/s, Angular Velocity: {angular_velocity:.2f} rad/s'

        try:
            self.client_socket.sendall(message.encode())
            self.get_logger().info(f'Message envoyé: {message}')
        except Exception as e:
            self.get_logger().error(f'Échec de l\'envoi du message: {e}')

    def check_connection(self):
        # Vérifiez la connexion toutes les 5 secondes
        if self.client_socket is None or self.client_socket.fileno() == -1:
            self.get_logger().warn('Reconnecter au serveur TCP')
            self.connect_to_server()

def main(args=None):
    rclpy.init(args=args)
    node = VelocityTcpSenderNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()

