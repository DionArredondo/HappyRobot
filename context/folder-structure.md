HappyRobot/
│
├── .env                        # Variables de entorno globales (API Keys, DB URLs)
├── docker-compose.yml          # Orquestador local de contenedores Docker
├── README.md                   # Documentación general y pasos de replicación
│
├── backend/                    # Servicio de FastAPI
│   ├── Dockerfile
│   ├── requirements.txt        # fastapi, uvicorn, httpx, pydantic, supabase
│   ├── main.py                 # Inicialización de la app y middlewares de seguridad
│   ├── database.py             # Conexión y cliente de Supabase
│   ├── models.py               # Modelos de Pydantic (Load, CallLog)
│   └── routers/
│       ├── vetting.py          # Endpoint: /validate-mc
│       ├── matching.py         # Endpoint: /loads/search
│       └── negotiation.py      # Endpoints: /negotiate y /webhooks/call-ended
│
├── frontend/                   # Streamlit service (Dashboard)
│   ├── Dockerfile
│   ├── requirements.txt        # streamlit, supabase, pandas, plotly
│   └── app.py                  # Interfaz gráfica y gráficas de métricas
│
└── context/                    # Context files for Cursor / VS Code
    ├── architecture.md         # El documento de arquitectura que generamos antes
    └── SKILLS.md               # Instrucciones de codificación y lógica algorítmica


# Project Directory Mappings

* `backend/main.py`: Handles core application bootstrap, environment setups, and security key authorization middlewares.
* `backend/database.py`: Establishes connections and connection pool runtimes targeting the Supabase infrastructure.
* `backend/models.py`: Declares data validation rules leveraging Pydantic syntax.
* `backend/router/vetting.py`: Manages credentials execution and logic workflows targeting external FMCSA parameters.
* `backend/router/matching.py`: Executes dynamic and fallback relational queries across the central freight inventory database.
* `backend/router/negotiation.py`: Runs calculation workflows across bargaining operations and ingests automated session conclusion events.
* `frontend/app.py`: Compiles the operations view charts layer using Streamlit scripts to query database insights.