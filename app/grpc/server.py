import os
import grpc
from concurrent import futures
from datetime import datetime, timedelta

from app.database import SessionLocal, init_db
from app import models
from . import catalogue_pb2, catalogue_pb2_grpc


class CatalogueServiceServicer(catalogue_pb2_grpc.CatalogueServiceServicer):

    def GetAllItems(self, request, context):
        """gRPC service for managing catalogue items"""
        db = SessionLocal()
        try:
            items = db.query(models.Item).all()
            now = datetime.utcnow()
            response = catalogue_pb2.ItemList()

            for item in items:
                remaining = max(int((item.end_time - now).total_seconds()), 0)
                response.items.add(
                    id=int(item.id),
                    title=item.title,
                    description=item.description,
                    starting_price=int(item.starting_price),
                    current_price=int(item.current_price),
                    active=bool(item.active),
                    duration_hours=int(item.duration_hours),
                    created_at=item.created_at.isoformat(),
                    end_time=item.end_time.isoformat() if item.end_time else "",
                    seller_id=int(item.seller_id),
                    shipping_cost=int(float(item.shipping_cost or 0)),
                    shipping_time=int(float(item.shipping_time or 0)),
                    remaining_time_seconds=int(remaining),
                )
            return response
        finally:
            db.close()

    def SearchItems(self, request, context):
        """Search items by keyword from the title"""
        db = SessionLocal()
        try:
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
                    id=int(item.id),
                    title=item.title,
                    description=item.description,
                    starting_price=int(item.starting_price),
                    current_price=int(item.current_price),
                    active=bool(item.active),
                    duration_hours=int(item.duration_hours),
                    created_at=item.created_at.isoformat(),
                    end_time=item.end_time.isoformat() if item.end_time else "",
                    seller_id=int(item.seller_id),
                    shipping_cost=int(float(item.shipping_cost or 0)),
                    shipping_time=int(float(item.shipping_time or 0)),
                    remaining_time_seconds=int(remaining),
                )
            return response
        finally:
            db.close()

    def GetItem(self, request, context):
        """Get a single item by specific item ID"""
        db = SessionLocal()
        try:
            item = db.query(models.Item).filter(models.Item.id == request.id).first()

            if not item:
                context.abort(
                    grpc.StatusCode.NOT_FOUND, f"Item with id {request.id} not found"
                )

            now = datetime.utcnow()
            remaining = max(int((item.end_time - now).total_seconds()), 0)

            return catalogue_pb2.ItemResponse(
                id=int(item.id),
                title=item.title,
                description=item.description,
                starting_price=int(item.starting_price),
                current_price=int(item.current_price),
                active=bool(item.active),
                duration_hours=int(item.duration_hours),
                created_at=item.created_at.isoformat(),
                end_time=item.end_time.isoformat() if item.end_time else "",
                seller_id=int(item.seller_id),
                shipping_cost=int(float(item.shipping_cost or 0)),
                shipping_time=int(float(item.shipping_time or 0)),
                remaining_time_seconds=int(remaining),
            )
        finally:
            db.close()

    def CreateItem(self, request, context):
        """Create a new item in the catalogue"""
        db = SessionLocal()
        try:
            if not request.title.strip():
                context.abort(grpc.StatusCode.INVALID_ARGUMENT, "Title is required")
            if not request.description.strip():
                context.abort(
                    grpc.StatusCode.INVALID_ARGUMENT, "Description is required"
                )
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
                id=int(new_item.id),
                title=new_item.title,
                description=new_item.description,
                starting_price=int(new_item.starting_price),
                current_price=int(new_item.current_price),
                active=bool(new_item.active),
                duration_hours=int(new_item.duration_hours),
                created_at=new_item.created_at.isoformat(),
                end_time=new_item.end_time.isoformat() if new_item.end_time else "",
                seller_id=int(new_item.seller_id),
                shipping_cost=int(float(new_item.shipping_cost or 0)),
                shipping_time=int(float(new_item.shipping_time or 0)),
                remaining_time_seconds=int(remaining),
            )
        finally:
            db.close()

    def DeactivateItem(self, request, context):
        db = SessionLocal()

        item = db.query(models.Item).filter(models.Item.id == request.id).first()

        if not item:
            context.abort(
                grpc.StatusCode.NOT_FOUND,
                f"Item with id {request.id} not found"
            )

        item.active = False
        db.commit()

        return catalogue_pb2.DeactivateItemResponse(
            success=True,
            message=f"Item {request.id} deactivated successfully"
        )



def serve():
    print("Initializing database tables...")
    init_db()
    print("Database tables ready!")

    port = os.getenv("GRPC_PORT", "50051")
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    catalogue_pb2_grpc.add_CatalogueServiceServicer_to_server(
        CatalogueServiceServicer(), server
    )
    server.add_insecure_port(f"[::]:{port}")
    print(f"gRPC CatalogueService running on port {port}")
    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
