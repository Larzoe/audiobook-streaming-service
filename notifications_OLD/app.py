from concurrent import futures
import grpc
import notification_pb2
import notification_pb2_grpc

class NotificationService(notification_pb2_grpc.NotificationServiceServicer):
    def SendNotification(self, request, context):
        # Logic to send notification
        print(f"Sending notification to {request.userId}: {request.message}")
        return notification_pb2.NotificationResponse(result='Notification sent successfully!')

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    notification_pb2_grpc.add_NotificationServiceServicer_to_server(NotificationService(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
