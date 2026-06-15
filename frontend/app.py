import streamlit as st
import httpx
import os
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from dotenv import load_dotenv

# Load environment variables at the absolute top
load_dotenv()

# Read configuration from environment
BACKEND_API_URL = os.getenv("BACKEND_API_URL")
BACKEND_API_KEY = os.getenv("BACKEND_API_KEY")

# Safety check for required environment variables
if not BACKEND_API_URL or not BACKEND_API_KEY:
    st.error(
        "⚠️ **Configuration Error**: Missing required environment variables. "
        "Please ensure `BACKEND_API_URL` and `BACKEND_API_KEY` are set in your frontend `.env` file."
    )
    st.stop()

# Configure page layout
st.set_page_config(
    page_title="HappyRobot Carrier Sales",
    layout="wide"
)

# Function to check API health
@st.cache_data(ttl=30)
def check_api_status():
    """Check if backend API is healthy."""
    try:
        response = httpx.get(
            f"{BACKEND_API_URL}/",
            headers={"X-API-KEY": BACKEND_API_KEY},
            timeout=5.0
        )
        return response.status_code == 200
    except Exception:
        return False

# Function to fetch all loads
@st.cache_data(ttl=60)
def fetch_all_loads():
    """Fetch all active loads from the backend."""
    try:
        response = httpx.get(
            f"{BACKEND_API_URL}/loads/search",
            headers={"X-API-KEY": BACKEND_API_KEY},
            timeout=10.0
        )
        if response.status_code == 200:
            data = response.json()
            if data:
                df = pd.DataFrame(data)
                return df
            else:
                return None
        else:
            return None
    except Exception as e:
        st.warning(f"Error fetching loads: {str(e)}")
        return None

# Helper function for carrier vetting
def validate_mc(mc_number):
    """Validate carrier MC number against backend vetting service."""
    try:
        response = httpx.post(
            f"{BACKEND_API_URL}/validate-mc",
            headers={"X-API-KEY": BACKEND_API_KEY},
            json={"carrier_mc": mc_number},
            timeout=10.0
        )
        if response.status_code == 200:
            return response.json()
        else:
            return {"eligible": False, "error": "Validation failed"}
    except Exception as e:
        return {"eligible": False, "error": str(e)}

# Helper function for searching loads with filters
def search_matching_loads(origin, destination, equipment_type):
    """Search for matching loads with filters."""
    try:
        params = {}
        if origin:
            params["origin"] = origin
        if destination:
            params["destination"] = destination
        if equipment_type:
            params["equipment_type"] = equipment_type
        
        response = httpx.get(
            f"{BACKEND_API_URL}/loads/search",
            headers={"X-API-KEY": BACKEND_API_KEY},
            params=params,
            timeout=10.0
        )
        if response.status_code == 200:
            data = response.json()
            return data
        else:
            return None
    except Exception as e:
        st.error(f"Error searching loads: {str(e)}")
        return None

# Helper function for price negotiation
def negotiate_load(load_id, counter_offer):
    """Submit counter offer for load negotiation."""
    try:
        response = httpx.post(
            f"{BACKEND_API_URL}/negotiate",
            headers={"X-API-KEY": BACKEND_API_KEY},
            json={"load_id": load_id, "counter_offer": counter_offer},
            timeout=10.0
        )
        if response.status_code == 200:
            return response.json()
        else:
            return {"status": "ERROR", "message": "Negotiation failed"}
    except Exception as e:
        return {"status": "ERROR", "message": str(e)}

# Helper function for submitting call logs
def submit_call_log(call_id, carrier_mc, load_id, duration, outcome, sentiment, final_rate=None):
    """Submit call log to backend."""
    try:
        response = httpx.post(
            f"{BACKEND_API_URL}/call-logs",
            headers={"X-API-KEY": BACKEND_API_KEY},
            json={
                "call_id": call_id,
                "carrier_mc": carrier_mc,
                "load_id": load_id,
                "final_rate": final_rate,
                "duration_seconds": duration,
                "outcome": outcome,
                "sentiment": sentiment
            },
            timeout=10.0
        )
        if response.status_code == 201:
            return True
        else:
            return False
    except Exception as e:
        st.error(f"Error submitting call log: {str(e)}")
        return False

# Helper function for fetching call logs
@st.cache_data(ttl=60)
def fetch_call_logs():
    """Fetch all call logs from the backend."""
    try:
        response = httpx.get(
            f"{BACKEND_API_URL}/call-logs",
            headers={"X-API-KEY": BACKEND_API_KEY},
            timeout=10.0
        )
        if response.status_code == 200:
            data = response.json()
            if data:
                # Handle both list and single object responses
                if isinstance(data, list):
                    df = pd.DataFrame(data)
                else:
                    df = pd.DataFrame([data])
                return df
            else:
                return None
        else:
            return None
    except Exception as e:
        st.warning(f"Error fetching call logs: {str(e)}")
        return None

# Initialize session state for voice bot simulator
if "mc_verified" not in st.session_state:
    st.session_state.mc_verified = False
if "matched_load" not in st.session_state:
    st.session_state.matched_load = None
if "negotiation_done" not in st.session_state:
    st.session_state.negotiation_done = False
if "final_call_data" not in st.session_state:
    st.session_state.final_call_data = None
if "final_rate" not in st.session_state:
    st.session_state.final_rate = None

# Sidebar setup
with st.sidebar:
    st.markdown("## 🤖 HappyRobot Inbound Sales PoC")
    st.markdown("---")
    
    # API Status Indicator
    api_healthy = check_api_status()
    if api_healthy:
        st.markdown("### 🟢 API Connected")
        st.caption("Backend is operational")
    else:
        st.markdown("### 🔴 API Offline")
        st.caption("Unable to reach backend service")
    
    st.markdown("---")
    st.info("Dashboard for real-time carrier sales operations and analytics")

# Main app layout
st.title("🚀 HappyRobot Carrier Sales Dashboard")
st.markdown("Real-time operations management and performance analytics")

# Tab structure
tab1, tab2, tab3 = st.tabs(["Active Freight Board", "Voice Bot Simulator", "Performance Analytics"])

with tab1:
    st.markdown("### 📋 Active Freight Board")
    
    # Fetch loads data
    loads_df = fetch_all_loads()
    
    if loads_df is not None and len(loads_df) > 0:
        # Interactive Metrics Section
        st.markdown("#### 📊 Key Metrics")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Active Loads", len(loads_df))
        
        with col2:
            avg_rate = loads_df["loadboard_rate"].mean() if "loadboard_rate" in loads_df.columns else 0
            st.metric("Average Rate", f"${avg_rate:,.2f}" if avg_rate > 0 else "N/A")
        
        with col3:
            if "destination" in loads_df.columns:
                top_destination = loads_df["destination"].mode()[0] if len(loads_df["destination"].mode()) > 0 else "N/A"
            else:
                top_destination = "N/A"
            st.metric("Top Destination", top_destination)
        
        st.markdown("---")
        
        # Search and Filter Section
        st.markdown("#### 🔍 Filter & Search")
        col_filter1, col_filter2 = st.columns(2)
        
        with col_filter1:
            origin_filter = st.text_input(
                "Filter by Origin",
                placeholder="Enter origin (e.g., New York)",
                key="origin_filter"
            )
        
        with col_filter2:
            equipment_options = ["All"]
            if "equipment_type" in loads_df.columns:
                equipment_options.extend(loads_df["equipment_type"].unique().tolist())
            equipment_filter = st.selectbox(
                "Filter by Equipment Type",
                options=equipment_options,
                key="equipment_filter"
            )
        
        # Apply filters
        filtered_df = loads_df.copy()
        
        if origin_filter:
            filtered_df = filtered_df[
                filtered_df.get("origin", "").str.contains(origin_filter, case=False, na=False)
            ]
        
        if equipment_filter != "All":
            filtered_df = filtered_df[filtered_df["equipment_type"] == equipment_filter]
        
        st.markdown("---")
        
        # Display filtered dataframe
        st.markdown(f"#### 📦 Showing {len(filtered_df)} of {len(loads_df)} Active Loads")
        st.dataframe(filtered_df, width='stretch')
        
    else:
        st.warning("⚠️ No active loads available or unable to fetch data from the backend.")

with tab2:
    st.markdown("### 🎙️ Voice Bot Simulator")
    st.markdown("Simulate a complete inbound carrier sales call workflow")
    
    # ============================================================================
    # STEP 1: CARRIER VETTING FORM
    # ============================================================================
    st.markdown("#### Step 1: 🔐 Carrier Vetting Check")
    st.markdown("Enter your MC number to verify carrier eligibility")
    
    col_mc1, col_mc2 = st.columns([3, 1])
    with col_mc1:
        mc_input = st.text_input(
            "Carrier MC Number",
            placeholder="e.g., 123456",
            key="mc_input"
        )
    
    with col_mc2:
        vet_button = st.button("1. Run Vetting Check", key="vet_button")
    
    if vet_button and mc_input:
        with st.spinner("Validating carrier..."):
            vet_result = validate_mc(mc_input)
            if vet_result.get("eligible"):
                st.session_state.mc_verified = True
                st.session_state.mc_number = mc_input
                st.success("✅ Carrier Verified & Eligible! Proceeding to load matching...")
            else:
                st.error("❌ Carrier Fraud/Ineligible. Call Terminated.")
                st.session_state.mc_verified = False
    
    if not st.session_state.mc_verified:
        st.info("ℹ️ Complete Step 1 to unlock the remaining steps")
        st.stop()
    
    st.markdown("---")
    
    # ============================================================================
    # STEP 2: INBOUND LOAD MATCHING
    # ============================================================================
    st.markdown("#### Step 2: 📦 Inbound Load Matching")
    st.markdown("Search for available freight matching your requirements")
    
    col_search1, col_search2, col_search3 = st.columns(3)
    with col_search1:
        origin_input = st.text_input("Origin", placeholder="e.g., New York", key="origin_input")
    with col_search2:
        destination_input = st.text_input("Destination", placeholder="e.g., Los Angeles", key="destination_input")
    with col_search3:
        equipment_input = st.text_input("Equipment Type", placeholder="e.g., Dry Van", key="equipment_input")
    
    search_button = st.button("2. Search Matching Loads", key="search_button")
    
    if search_button:
        with st.spinner("Searching for matching loads..."):
            matching_data = search_matching_loads(origin_input, destination_input, equipment_input)
            if matching_data:
                # Handle both list and single object responses
                if isinstance(matching_data, list):
                    loads_list = matching_data
                else:
                    loads_list = [matching_data]
                
                if len(loads_list) > 0:
                    # Use first matching load
                    matched_load = loads_list[0]
                    st.session_state.matched_load = matched_load
                    
                    st.success(f"✅ Found {len(loads_list)} matching load(s)!")
                    
                    st.markdown("##### Best Match Load Details:")
                    col_load1, col_load2, col_load3 = st.columns(3)
                    with col_load1:
                        st.metric("Load ID", matched_load.get("id", "N/A"))
                    with col_load2:
                        route = f"{matched_load.get('origin', 'N/A')} → {matched_load.get('destination', 'N/A')}"
                        st.metric("Route", route)
                    with col_load3:
                        rate = matched_load.get("loadboard_rate", 0)
                        st.metric("Rate", f"${rate:,.2f}" if rate > 0 else "N/A")
                    
                    st.json(matched_load)
                else:
                    st.warning("⚠️ No matching loads found. Try different filters.")
            else:
                st.error("❌ Failed to search loads. Please try again.")
    
    if st.session_state.matched_load is None:
        st.info("ℹ️ Complete Step 2 to unlock negotiation")
        st.stop()
    
    st.markdown("---")
    
    # ============================================================================
    # STEP 3: BOUNDED PRICE NEGOTIATION
    # ============================================================================
    st.markdown("#### Step 3: 💰 Bounded Price Negotiation")
    st.markdown("Submit your counter offer for the matched load")
    
    current_rate = st.session_state.matched_load.get("loadboard_rate", 0)
    st.info(f"📊 Current Loadboard Rate: **${current_rate:,.2f}**")
    
    col_nego1, col_nego2 = st.columns([3, 1])
    with col_nego1:
        counter_offer = st.number_input(
            "Your Counter Offer ($)",
            min_value=100.0,
            value=float(current_rate),
            step=100.0,
            key="counter_offer"
        )
    
    with col_nego2:
        nego_button = st.button("3. Submit Counter Offer", key="nego_button")
    
    if nego_button:
        load_id = st.session_state.matched_load.get("load_id")
        with st.spinner("Processing negotiation..."):
            nego_result = negotiate_load(load_id, counter_offer)
            st.session_state.final_call_data = nego_result
            st.session_state.final_rate = counter_offer  # Store counter_offer as final_rate for Step 4
            
            status = nego_result.get("status", "ERROR")
            
            if status == "ACCEPTED":
                st.success(f"🎉 **NEGOTIATION ACCEPTED!** Load confirmed at ${counter_offer:,.2f}")
                st.session_state.negotiation_done = True
            elif status == "COUNTER":
                bot_counter = nego_result.get("counter_offer", current_rate)
                st.info(f"🔄 **BOT COUNTER-OFFER** The bot countered at ${bot_counter:,.2f}")
            elif status == "REJECTED":
                st.error(f"❌ **OFFER REJECTED** Rate is too low. Minimum: ${nego_result.get('min_rate', current_rate):,.2f}")
            else:
                st.error(f"❌ **NEGOTIATION ERROR**: {nego_result.get('message', 'Unknown error')}")
    
    st.markdown("---")
    
    # ============================================================================
    # STEP 4: SUBMIT CALL LOG
    # ============================================================================
    st.markdown("#### Step 4: 📝 Terminate & Log Call")
    st.markdown("Submit the call to the system for record-keeping")
    
    if st.session_state.final_call_data is None:
        st.info("ℹ️ Complete Step 3 negotiation before logging the call")
    else:
        # Auto-generate call data
        import random
        duration = random.randint(120, 900)  # Random duration 2-15 minutes
        outcome = st.session_state.final_call_data.get("status", "NEUTRAL")
        sentiment = "POSITIVE" if outcome == "ACCEPTED" else "NEUTRAL"
        
        col_log1, col_log2, col_log3 = st.columns(3)
        with col_log1:
            st.metric("Call Duration", f"{duration} sec")
        with col_log2:
            st.metric("Outcome", outcome)
        with col_log3:
            st.metric("Sentiment", sentiment)
        
        log_button = st.button("4. Terminate and Log Call", key="log_button")
        
        if log_button:
            with st.spinner("Logging call to system..."):
                import uuid
                call_id = str(uuid.uuid4())  # Generate unique call ID
                final_rate = st.session_state.get("final_rate", None)  # Retrieve counter_offer from session state
                
                success = submit_call_log(
                    call_id=call_id,
                    carrier_mc=st.session_state.mc_number,
                    load_id=st.session_state.matched_load.get("id"),
                    duration=duration,
                    outcome=outcome,
                    sentiment=sentiment,
                    final_rate=final_rate
                )
                
                if success:
                    st.success("🚀 Call successfully logged to Supabase!")
                    st.balloons()
                else:
                    st.error("❌ Failed to log call. Please try again.")

with tab3:
    st.markdown("### 📊 Performance Analytics")
    st.markdown("Real-time insights into carrier sales performance and call metrics")
    
    # Fetch call logs data
    logs_df = fetch_call_logs()
    
    if logs_df is not None and len(logs_df) > 0:
        # Calculate key metrics
        total_calls = len(logs_df)
        
        # Average call duration
        if "duration" in logs_df.columns:
            avg_duration = logs_df["duration"].mean()
        else:
            avg_duration = 0
        
        # Conversion rate (BOOKED calls / total calls)
        if "outcome" in logs_df.columns:
            booked_calls = len(logs_df[logs_df["outcome"] == "BOOKED"])
            conversion_rate = (booked_calls / total_calls * 100) if total_calls > 0 else 0
        else:
            conversion_rate = 0
        
        # Display key metrics
        st.markdown("#### 📈 Key Operational Metrics")
        metric_col1, metric_col2 = st.columns(2)
        
        with metric_col1:
            st.metric("Average Call Duration (seconds)", f"{avg_duration:.0f}s")
        
        with metric_col2:
            st.metric("Conversion Rate (%)", f"{conversion_rate:.1f}%")
        
        st.markdown("---")
        
        # Create visualizations in two columns
        st.markdown("#### 📉 Performance Visualizations")
        viz_col1, viz_col2 = st.columns(2)
        
        # Chart 1: Call Volume by Outcome (Bar Chart)
        with viz_col1:
            if "outcome" in logs_df.columns:
                outcome_counts = logs_df["outcome"].value_counts().reset_index()
                outcome_counts.columns = ["Outcome", "Count"]
                
                fig_outcome = px.bar(
                    outcome_counts,
                    x="Outcome",
                    y="Count",
                    title="Call Volume by Outcome",
                    labels={"Count": "Number of Calls", "Outcome": "Call Outcome"},
                    color="Outcome",
                    color_discrete_sequence=px.colors.qualitative.Set2
                )
                fig_outcome.update_layout(
                    xaxis_title="Outcome",
                    yaxis_title="Number of Calls",
                    height=400,
                    showlegend=False
                )
                st.plotly_chart(fig_outcome, width='stretch')
            else:
                st.warning("Outcome data not available")
        
        # Chart 2: Sentiment Distribution (Donut Chart)
        with viz_col2:
            if "sentiment" in logs_df.columns:
                sentiment_counts = logs_df["sentiment"].value_counts().reset_index()
                sentiment_counts.columns = ["Sentiment", "Count"]
                
                fig_sentiment = px.pie(
                    sentiment_counts,
                    values="Count",
                    names="Sentiment",
                    title="Carrier Sentiment Distribution",
                    hole=0.4,
                    color_discrete_sequence=px.colors.qualitative.Set2
                )
                fig_sentiment.update_layout(height=400)
                st.plotly_chart(fig_sentiment, width='stretch')
            else:
                st.warning("Sentiment data not available")
        
        st.markdown("---")
        
        # Summary statistics table
        st.markdown("#### 📋 Summary Statistics")
        summary_data = {
            "Metric": ["Total Calls", "Average Duration (s)", "Conversion Rate (%)", "Total Carriers"],
            "Value": [
                total_calls,
                f"{avg_duration:.0f}",
                f"{conversion_rate:.1f}",
                logs_df["mc"].nunique() if "mc" in logs_df.columns else "N/A"
            ]
        }
        summary_df = pd.DataFrame(summary_data)
        st.dataframe(summary_df, width='stretch', hide_index=True)
        
    else:
        st.warning("⚠️ No call logs available yet. Start simulating calls to see performance analytics.")
