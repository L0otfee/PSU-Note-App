# PSU Note App

แอปพลิเคชันจดบันทึกแบบ Web-based ที่พัฒนาด้วย Flask และ PostgreSQL สำหรับจัดการโน้ตและ tags

## License

- **จัดการโน้ต**: สร้าง, แก้ไข, ลบโน้ต
- **ระบบ Tags**: จัดการและจัดหมวดหมู่โน้ตด้วย tags
- **ค้นหาโน้ต**: ค้นหาโน้ตผ่าน tags
- **ลบแบบ Bulk**: ลบโน้ตหรือ tags ทั้งหมดพร้อมกัน
- **ความปลอดภัย**: จัดการ Foreign Key Constraints อย่างถูกต้อง
- **ภาษาไทย**: รองรับการแสดงผลภาษาไทยครบถ้วน

## เทคโนโลยีที่ใช้

- **Backend**: Flask (Python)
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy
- **Forms**: Flask-WTF
- **Frontend**: HTML Templates (Jinja2)
- **Encoding**: UTF-8 support

## โครงสร้างโปรเจค

```
psunote/
├── psunote/
│   ├── noteapp.py          # Main Flask application
│   ├── models.py           # Database models
│   ├── forms.py            # WTF Forms
│   ├── templates/          # HTML templates
│      ├── index.html
│      ├── notes-create.html
│      ├── notes-edit.html
│      ├── tags-list.html
│      ├── tags-edit.html
│      └── tags-view.html
│   
│   
├── requirements.txt        # Python dependencies
└── README.md              # Documentation
```

## โครงสร้างฐานข้อมูล

### ตาราง `notes`

| Field        | Type     | Description                        |
| ------------ | -------- | ---------------------------------- |
| id           | INTEGER  | Primary Key                        |
| title        | VARCHAR  | ชื่อโน้ต                   |
| description  | TEXT     | เนื้อหาโน้ต             |
| created_date | DATETIME | วันที่สร้าง             |
| updated_date | DATETIME | วันที่แก้ไขล่าสุด |

### ตาราง `tags`

| Field        | Type     | Description                 |
| ------------ | -------- | --------------------------- |
| id           | INTEGER  | Primary Key                 |
| name         | VARCHAR  | ชื่อ tag (ไม่ซ้ำ) |
| created_date | DATETIME | วันที่สร้าง      |

### ตาราง `note_tag` (Many-to-Many)

| Field   | Type    | Description             |
| ------- | ------- | ----------------------- |
| note_id | INTEGER | Foreign Key → notes.id |
| tag_id  | INTEGER | Foreign Key → tags.id  |

## การติดตั้งและรัน

### 1. ข้อกำหนดเบื้องต้น

- Python 3.8+
- PostgreSQL 12+
- pip (Python package manager)

### 2. ติดตั้ง Dependencies

```bash
cd psunote
pip install -r requirements.txt
```

### 3. ตั้งค่าฐานข้อมูล PostgreSQL

#### สร้างฐานข้อมูลและผู้ใช้:

```sql
-- เข้า PostgreSQL console
psql -U postgres

-- สร้างผู้ใช้และฐานข้อมูล
CREATE USER coe WITH PASSWORD 'CoEpasswd';
CREATE DATABASE coedb OWNER coe;
GRANT ALL PRIVILEGES ON DATABASE coedb TO coe;
```

### 4. รันแอปพลิเคชัน

```bash
cd psunote
python noteapp.py
```

เปิดเว็บเบราว์เซอร์ไปที่: **http://127.0.0.1:5000**

## ตัวอย่างหน้าเว็ป ![1754162831082](image/README/1754162831082.png)

## API Endpoints

### Notes Management

- `GET /` - หน้าหลัก (รายการโน้ต)
- `GET/POST /notes/create` - สร้างโน้ตใหม่
- `GET/POST /notes/<id>/edit` - แก้ไขโน้ต
- `POST /notes/<id>/delete` - ลบโน้ต
- `POST /notes/delete-all` - ลบโน้ตทั้งหมด

### Tags Management

- `GET /tags` - รายการ tags
- `GET/POST /tags/<id>/edit` - แก้ไข tag
- `POST /tags/<id>/delete` - ลบ tag
- `POST /tags/delete-all` - ลบ tags ทั้งหมด
- `GET /tags/<name>` - ดูโน้ตที่มี tag นี้

### Bulk Operations

- `POST /delete-all` - ลบข้อมูลทั้งหมด (โน้ต + tags)

## การจัดการฐานข้อมูลด้วย pgAdmin

### ติดตั้ง pgAdmin ด้วย Docker:

```bash
docker run --name pgadmin-container \
  -p 8080:80 \
  -e 'PGADMIN_DEFAULT_EMAIL=admin@admin.com' \
  -e 'PGADMIN_DEFAULT_PASSWORD=admin123' \
  -d dpage/pgadmin4
```

### เข้าใช้ pgAdmin:

1. เปิด: **http://localhost:8080**
2. Login: `admin@admin.com` / `admin123`
3. เพิ่ม Server:
   - **Host**: `host.docker.internal` (Docker) หรือ `localhost`
   - **Port**: `5432`
   - **Database**: `coedb`
   - **Username**: `coe`
   - **Password**: `CoEpasswd`

## การตรวจสอบข้อมูลด้วย psql

```bash
# เชื่อมต่อฐานข้อมูล
psql postgresql://coe:CoEpasswd@localhost:5432/coedb

# ดูรายการตาราง
\dt

# ดูข้อมูลโน้ต
SELECT * FROM notes;

# ดูข้อมูล tags
SELECT * FROM tags;

# ดูความสัมพันธ์ notes-tags
SELECT n.title, array_agg(t.name) as tags 
FROM notes n 
LEFT JOIN note_tag nt ON n.id = nt.note_id 
LEFT JOIN tags t ON nt.tag_id = t.id 
GROUP BY n.id, n.title;
```

## การพัฒนาเพิ่มเติม

### ฟีเจอร์ที่สามารถเพิ่มได้:

- ระบบค้นหาขั้นสูง
- ระบบผู้ใช้และการล็อกอิน
- UI/UX ที่สวยงาม
- Responsive design
- ระบบแจ้งเตือน
- Export/Import ข้อมูล
- API Authentication

## ผู้พัฒนา

พัฒนาโดย: ลุตฟี ซาและ
วันที่: 1 สิงหาคม 2025
Version: 1.0.0

---

**หมายเหตุ**: โปรเจคนี้พัฒนาเพื่อการศึกษาและสามารถนำไปต่อยอดได้ตามต้องการ
