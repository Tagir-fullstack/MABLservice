from psycopg import AsyncConnection
from datetime import datetime

# Удалено: from scipy._lib.cobyqa import problem
# Был неиспользуемый импорт из scipy — к проекту отношения не имеет


class Request:
    def __init__(self, connector: AsyncConnection):
        self.connector = connector

    async def add_data(self, name: str, phone: str, device: str, problem: str, status: str) -> int:
        query = """
            INSERT INTO orders (name, phone, device, problem, status)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id;
        """
        async with self.connector.cursor() as cursor:
            await cursor.execute(query, (name, phone, device, problem, status))
            row = await cursor.fetchone()
            await self.connector.commit()
            return row[0]


    async def add_old_order(self, id: int, name: str, phone: str, device: str, problem: str, status: str):
        query = """
            INSERT INTO orders (id, name, phone, device, problem, status)
            VALUES (%s, %s, %s, %s, %s, %s);
        """
        async with self.connector.cursor() as cursor:
            await cursor.execute(query, (id, name, phone, device, problem, status))
            await self.connector.commit()

    async def sync_order_sequence(self):
        query = "SELECT setval('orders_id_seq', (SELECT MAX(id) FROM orders))"
        async with self.connector.cursor() as cursor:
            await cursor.execute(query)
            await self.connector.commit()

    async def get_order(self, id: int):
        query = "SELECT id, name, phone, device, problem, status, created_at FROM orders WHERE id = %s ORDER BY created_at"
        async with self.connector.cursor() as cursor:
            await cursor.execute(query, (id,))
            row = await cursor.fetchone()

            if not row:
                return None

            created_at: datetime = row[6]
            formatted_time = created_at.strftime("%d.%m.%y %H:%M")

            order = {
                "id": row[0],
                "name": row[1],
                "phone": row[2],
                "device": row[3],
                "problem": row[4],
                "status": row[5],
                "created_at": formatted_time
            }

            return order


    async def get_order_by_name(self, name: str):
        query = """SELECT id, device, status, to_char(created_at, 'DD.MM.YY HH24:MI') as created_at 
                   FROM orders 
                   WHERE name = %s 
                   ORDER BY id ASC"""
        async with self.connector.cursor() as cursor:
            await cursor.execute(query, (name,))
            rows = await cursor.fetchall()

            orders = []
            for row in rows:
                orders.append({
                    "id": row[0],
                    "device": row[1],
                    "status": row[2],
                    "created_at": row[3]
                })

            return orders


    async def get_order_by_phone(self, phone_suffix: str):
        query = """SELECT id, name, device, to_char(created_at, 'DD.MM.YY HH24:MI') as created_at 
                   FROM orders 
                   WHERE phone LIKE %s 
                   ORDER BY id ASC"""
        async with self.connector.cursor() as cursor:
            await cursor.execute(query, (f"%{phone_suffix}",))
            rows = await cursor.fetchall()

            orders = []
            for row in rows:
                orders.append({
                    "id": row[0],
                    "name": row[1],
                    "device": row[2],
                    "created_at": row[3]
                })

            return orders



    async def get_next_order_id(self) -> int:
        query = "SELECT last_value + 1 FROM orders_id_seq"
        async with self.connector.cursor() as cursor:
            await cursor.execute(query)
            row = await cursor.fetchone()
            return row[0]

################################################################################################################

    async def edit_name(self, name: str, id: int):
        query = "UPDATE orders SET name = %s WHERE id = %s"
        async with self.connector.cursor() as cursor:
            await cursor.execute(query, (name, id))
            await self.connector.commit()

    async def edit_phone(self, phone: str, id: int):
        query = "UPDATE orders SET phone = %s WHERE id = %s"
        async with self.connector.cursor() as cursor:
            await cursor.execute(query, (phone, id))
            await self.connector.commit()

    async def edit_device(self, device: str, id: int):
        query = "UPDATE orders SET device = %s WHERE id = %s"
        async with self.connector.cursor() as cursor:
            await cursor.execute(query, (device, id))
            await self.connector.commit()

    async def edit_problem(self, problem: str, id: int):
        query = "UPDATE orders SET problem = %s WHERE id = %s"
        async with self.connector.cursor() as cursor:
            await cursor.execute(query, (problem, id))
            await self.connector.commit()


    async def finish_status(self, status: str, id: int):
        query = "UPDATE orders SET status = %s WHERE id = %s"
        async with self.connector.cursor() as cursor:
            await cursor.execute(query, (status, id))
            await self.connector.commit()


################################################################################################################

    async def add_comments(self, order_id: int, comment: str, editor: str):
        query = """
            INSERT INTO comments (order_id, comment, editor) 
            VALUES (%s, %s, %s);
        """
        async with self.connector.cursor() as cursor:
            await cursor.execute(query, (order_id, comment, editor))
            await self.connector.commit()

    async def get_comments(self, order_id: int):
        query = "SELECT editor, created_at, comment FROM comments WHERE order_id = %s ORDER BY created_at"
        async with self.connector.cursor() as cursor:
            await cursor.execute(query, (order_id, ))
            rows = await cursor.fetchall()

            comments = []
            for row in rows:
                created_at: datetime = row[1]  # это datetime
                formatted_time = created_at.strftime("%d.%m.%y %H:%M")
                comments.append({
                    "editor": row[0],
                    "comment": row[2],
                    "created_at": formatted_time
                })

            return comments


###################################################################################################################


    async def get_client_order_by_name(self,id: int, name: str):
        query = """SELECT id, name, device, status, to_char(created_at, 'DD.MM.YY HH24:MI') as created_at 
                   FROM orders 
                   WHERE id = %s AND name = %s
                   ORDER BY id ASC"""
        async with self.connector.cursor() as cursor:
            await cursor.execute(query, (id, name))
            row = await cursor.fetchone()

            if not row:
                return None

            order = {
                "id": row[0],
                "name": row[1],
                "device": row[2],
                "status": row[3],
                "created_at": row[4]
            }

            return order


    async def get_client_order_by_phone(self, id: int, phone_suffix: str):
        query = """SELECT id, name, device, status, to_char(created_at, 'DD.MM.YY HH24:MI') as created_at 
                   FROM orders 
                   WHERE id = %s 
                   AND RIGHT(phone, LENGTH(%s)) = %s"""
        async with self.connector.cursor() as cursor:
            await cursor.execute(query, (id, phone_suffix, phone_suffix))
            row = await cursor.fetchone()

            if not row:
                return None

            order = {
                "id": row[0],
                "name": row[1],
                "device": row[2],
                "status": row[3],
                "created_at": row[4]
            }

            return order