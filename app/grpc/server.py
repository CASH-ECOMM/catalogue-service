import grpc
from concurrent import futures
from datetime import datetime, timedelta

from app.database import SessionLocal, init_db
from app import models
from . import catalogue_pb2, catalogue_pb2_grpc


class CatalogueServiceServicer(catalogue_pb2_grpc.CatalogueServiceServicer):
    def GetAllItems(self, request, context):
        db = SessionLocal()
        items = db.query(models.Item).all()
        now = datetime.utcnow()
        response = catalogue_pb2.ItemList()

        for item in items:
            remaining = max(int((item.end_time - now).total_seconds()), 0)
            response.items.add(
                id=item.id,
                title=item.title,
                description=item.description,
                starting_price=item.starting_price,
                current_price=item.current_price,
                active=item.active,
                duration_hours=item.duration_hours,
                created_at=item.created_at.isoformat(),
                end_time=item.end_time.isoformat() if item.end_time else "",
                seller_id=item.seller_id,
                shipping_cost=item.shipping_cost,
                shipping_time=item.shipping_time,
                remaining_time_seconds=remaining,
            )
        return response

    def SearchItems(self, request, context):
        db = SessionLocal()
        results = (
            db.query(models.Item)
            .filter(models.Item.title.ilike(f"%{request.keyword}%"))
            .all()
        )

        now = datetime.utcnow()
        response = catalogue_pb2.ItemList()

        for item in results:
            remaining = max(int((item.end_time - now).total_seconds()), 0)
            response.items.add(
                id=item.id,
                title=item.title,
                description=item.description,
                starting_price=item.starting_price,
                current_price=item.current_price,
                active=item.active,
                duration_hours=item.duration_hours,
                created_at=item.created_at.isoformat(),
                end_time=item.end_time.isoformat() if item.end_time else "",
                seller_id=item.seller_id,
                shipping_cost=item.shipping_cost,
                shipping_time=item.shipping_time,
                remaining_time_seconds=remaining,
            )
        return response

    def CreateItem(self, request, context):
        db = SessionLocal()

        if not request.title.strip():
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, "Title is required")
        if not request.description.strip():
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, "Description is required")
        if request.starting_price is None or request.starting_price <= 0:
            context.abort(
                grpc.StatusCode.INVALID_ARGUMENT,
                "Starting price must be greater than 0",
            )
        if request.duration_hours is None or request.duration_hours <= 0:
            context.abort(
                grpc.StatusCode.INVALID_ARGUMENT,
                "Duration hours must be greater than 0",
            )

        now = datetime.utcnow()
        end_time = now + timedelta(hours=request.duration_hours)

        new_item = models.Item(
            title=request.title,
            description=request.description,
            starting_price=request.starting_price,
            current_price=request.starting_price,
            duration_hours=request.duration_hours,
            created_at=now,
            end_time=end_time,
            seller_id=request.seller_id,
        )
        db.add(new_item)
        db.commit()
        db.refresh(new_item)

        remaining = max(int((end_time - now).total_seconds()), 0)

        return catalogue_pb2.ItemResponse(
            id=new_item.id,
            title=new_item.title,
            description=new_item.description,
            starting_price=new_item.starting_price,
            current_price=new_item.current_price,
            active=new_item.active,
            duration_hours=new_item.duration_hours,
            created_at=new_item.created_at.isoformat(),
            end_time=new_item.end_time.isoformat() if new_item.end_time else "",
            seller_id=new_item.seller_id,
            shipping_cost=new_item.shipping_cost,
            shipping_time=new_item.shipping_time,
            remaining_time_seconds=remaining,
        )


def serve():
    # Create database tables if they don't exist
    print("Initializing database tables...")
    init_db()
    print("Database tables ready!")

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    catalogue_pb2_grpc.add_CatalogueServiceServicer_to_server(
        CatalogueServiceServicer(), server
    )
    server.add_insecure_port("[::]:50051")
    print("gRPC CatalogueService running on port 50051")
    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
