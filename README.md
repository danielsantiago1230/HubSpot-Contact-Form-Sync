# HubSpot-Contact-Form-Sync

This project is a Django-based application that allows admin users to perform CRUD operations on contact information, which is automatically synced with HubSpot CRM using the `hubspot-api-client` library (version 11.1.0).

## Prerequisites

Before running the project, ensure you have the following environment variables set.

### Local Development Setup
Example environment files are provided and should be moved to the `hubspot_contact_form_sync/.envs/.local/` directory:

#### Django Environment Variables
Move `.env/.local/.django` to `hubspot_contact_form_sync/.envs/.local/.django` and edit the following keys:

```ini
HUBSPOT_ACCESS_TOKEN=<your_hubspot_access_token>
HUBSPOT_CLIENT_SECRET=<your_hubspot_client_secret>
```

#### PostgreSQL Environment Variables
Move `.env/.local/.postgres` to `hubspot_contact_form_sync/.envs/.local/.postgres` and edit the following keys:

```ini
POSTGRES_HOST=<your_postgres_host>
POSTGRES_PORT=<your_postgres_port>
POSTGRES_DB=<your_postgres_db>
POSTGRES_USER=<your_postgres_user>
POSTGRES_PASSWORD=<your_postgres_password>
```

## Installation and Setup

1️⃣ **Clone the Repository**

```sh
git clone https://github.com/danielsantiago1230/HubSpot-Contact-Form-Sync.git
cd HubSpot-Contact-Form-Sync
```

2️⃣ **Run Migrations**
Before creating a superuser, ensure the database is set up by running migrations:

```sh
docker-compose -f docker-compose.local.yml run --rm django python manage.py migrate
```

3️⃣ **Build and Run the Project**

```sh
docker-compose -f docker-compose.local.yml up --build
```

4️⃣ **Create a Superuser Account**
To access admin features, create a superuser account:

```sh
docker-compose -f docker-compose.local.yml run --rm django python manage.py createsuperuser
```

## Usage

- **Access the Application**:
  Open your browser and navigate to:
  [http://0.0.0.0:8000/hs_app/contacts/](http://0.0.0.0:8000/hs_app/contacts/)
  Note: Admin credentials are required to manage contacts.

## Forms and Templates

The application uses several forms located in the `hubspot_contact_form_sync/hubspot_contact_form_sync/templates/hs_app` directory:

- `contact_form.html` → For adding new contacts.
- `contact_list.html` → To view all contacts.
- `contact_update.html` → For updating existing contacts.
- `contact_success.html` → Confirmation page after adding a contact.
- `contact_delete.html` → For deleting contacts.

## 🚀 Production Deployment

To deploy the application in a production environment using AWS EC2, follow these steps:

1️⃣ **AWS Configuration**

**Create an EC2 Instance (First Time Setup Only)**
If you haven't created an EC2 instance yet, use this command:

```sh
aws ec2 run-instances --profile <your-aws-profile> \
    --image-id ami-005fc0f236362e99f \  # Ubuntu 22.04 LTS (Change if using another region)
    --count 1 \
    --instance-type t2.micro \  # Free-tier eligible
    --key-name <your-key-file-name> \  # Use your key pair
    --security-groups default \  # Modify for better security
    --region us-east-1  # Change if using another AWS region
```

**Start the EC2 Instance**

```sh
aws ec2 start-instances --profile <your-aws-profile> --instance-ids <your-instance-id>
```

**Retrieve the Public IP Address**

```sh
aws ec2 describe-instances --profile <your-aws-profile> \
    --query 'Reservations[*].Instances[*].{ID:InstanceId,State:State.Name,PublicIP:PublicIpAddress}'
```

2️⃣ **SSH into the Instance**
Once your EC2 instance is running, connect via SSH:

```sh
ssh -i <your-key-file>.pem ubuntu@<your-ec2-public-ip>
```

3️⃣ **Install Docker Engine**

```sh
sudo apt update && sudo apt install -y docker.io
```

Enable and start Docker:

```sh
sudo systemctl enable docker
sudo systemctl start docker
sudo systemctl status docker
```

4️⃣ **Install Docker Compose**

```sh
sudo apt update && sudo apt install -y docker-compose
```

Verify installation:

```sh
docker-compose --version
```

5️⃣ **Install Git & Clone Your Django Project**

```sh
sudo apt install -y git
git clone https://github.com/danielsantiago1230/HubSpot-Contact-Form-Sync.git
cd HubSpot-Contact-Form-Sync
```

6️⃣ **Set Up Environment Variables**

- **Move Environment Files:**
  - Move the example environment files to the production directory:
    ```sh
    mv .env/.production/.django hubspot_contact_form_sync/.envs/.production/.django
    mv .env/.production/.postgres hubspot_contact_form_sync/.envs/.production/.postgres
    mv .env/.production/.traefik hubspot_contact_form_sync/.envs/.production/.traefik
    ```

- **Update Environment Files:**
  - Open each file and replace placeholder values with your actual production values:
    - `hubspot_contact_form_sync/.envs/.production/.django`
    - `hubspot_contact_form_sync/.envs/.production/.postgres`
    - `hubspot_contact_form_sync/.envs/.production/.traefik`

7️⃣ **Run Migrations**

```sh
docker-compose -f docker-compose.production.yml run --rm django python manage.py migrate
```

8️⃣ **Create a Superuser Account**

```sh
docker-compose -f docker-compose.production.yml run --rm django python manage.py createsuperuser
```

9️⃣ **Restart the Production Containers**

```sh
docker-compose -f docker-compose.production.yml down
docker-compose -f docker-compose.production.yml up --build -d
```

🔟 **Verify the Deployment**

Once your containers are running, you can access the application:

- **Django Admin**: Navigate to `http://<your-ec2-public-ip>/DJANGO_ADMIN_URL` and sign in with the admin user you created.
- **Contacts Page**: After signing in, go to `http://<your-ec2-public-ip>/hs_app/contacts/` to manage contacts.

```sh
docker-compose -f docker-compose.production.yml logs -f
```

🛑 **Stopping the EC2 Instance to Avoid Charges**
To prevent unnecessary AWS charges, stop your EC2 instance when you're done:

```sh
aws ec2 stop-instances --profile <your-aws-profile> --instance-ids <your-instance-id>
```

*Keep in mind that every time you start the EC2 instance, you will have a new public IP address. and you will need to update the environment variables with the new IP address.*

**What's Not Included in This Deployment**

- 🚫 HTTPS (Traefik is configured for HTTP-only for simplicity)
- 🚫 AWS S3 for media storage (Django stores media files locally inside the container)
- 🚫 AWS RDS (PostgreSQL runs as a Docker container instead of an AWS-managed database)

➡️ If you need these features in the future, update the configurations accordingly.

## Contributing

Contributions are welcome! Fork the repository and submit a pull request.

## License

This project is licensed under the MIT License. See the `LICENSE` file for more details.
