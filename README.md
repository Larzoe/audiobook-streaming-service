# audiobook-streaming-service

**Microservices:**
* Payments
* Accounts 
* Catalog Management
* Publisher

**Service operations:**
* Payments: Payment created/updated/passed/failed
* Payments: Create payment Mollie (PSP) (SaaS)
* Accounts:  Activate/deactivate account
* Publisher: Book changed/added/deleted
* Catalog management: Book changed/added/deleted
* Notifications: Send notification
* Publisher: Upload book to Object Storage

**Two domains from design:**
* check

**Orchestration and Choreography use:**
* Orchestration:  Kubernetes for the services
* Choreography: Google Pub/Sub 

**Restful services:**
* PSP
* authentication provider
* Payments
* Accounts
* Catalog Management
* Publisher

**FaaS:** 
* Notification services 

**Simple service implementations:**
* Docker containers per service
* one per service, in different code bases
* one CloudSQL db + multiple schemas
* Object storage + CDN for media assets
* Google Cloud CI/CD + GitOps
* Deploying based on git repos	

**Assumptions made:**
* We will not use any analytics for this prototype.
* We will use external API’s for billing and payment.
* We assume that we use a CDN but no implemented as this implementation is trivial

**External APIs to use:**
* Firebase for Authentication
* Mollie as PSP
* Django/FastAPI for code bases
