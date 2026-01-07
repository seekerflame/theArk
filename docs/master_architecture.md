flowchart TB
    %% ======================================================================================
    %% 1. THE ARK: CIVILIZATION OS (Human/Logic Layers)
    %% ======================================================================================
    subgraph Gaia_UI["Gaia Interface (The Village)"]
        direction TB
        UI_Dash["📊 Dashboard (Pip-Boy)"]
        UI_Quests["📝 Quest Board (quests.json)"]
        UI_Wallet["🪙 AT Wallet"]
        UI_Studio["🏗️ Design Studio"]
        UI_Justice["⚖️ Justice Hub (justice.html)"]
        UI_Merch["🏪 Merchant Portal (kiosk.html)"]

        UI_Dash --> UI_Quests
        UI_Dash --> UI_Wallet
        UI_Dash --> UI_Merch
        UI_Quests --> UI_Studio
        UI_Dash --> UI_Justice
    end

    subgraph Ark_Core["The Ark Core (Logic)"]
        direction TB
        Ledger["📜 Ledger (SQLite)"]
        Identity["🆔 Identity Manager"]
        Config["🔐 Config (.env)"]
        
        subgraph Agents["Autonomous Agents"]
            Steward["🤖 Steward (Logic)"]
            Evol["🧬 Evolution Engine (Ollama)"]
        end

        Treasury["💰 Treasury (Mint)"]
        Fiat["💱 Fiat Bridge"]
        MerchAPI["🏪 Merchant Network"]
        Party["🎉 Social/Party Mode"]
        
        subgraph Board_Bored["Board Bored (Ad Network)"]
            BB_Portal["🖥️ Advertiser Portal"]
            BB_Mobile["📱 Mobile Engagement"]
            BB_Display["📺 Board Display"]
            BB_Analytics["📈 ROI Analytics"]
        end
    end

    subgraph Justice_Sys["Governance & Safety"]
        Gov["⚖️ Governance Engine"]
        ModAPI["🛡️ Moderation API"]
        Justice["⚖️ Justice Oracle"]
        Log["📜 Transparency Log"]
    end

    %% ======================================================================================
    %% 2. FRIEND'S ENGINEERING CORE (Physics/AI Layers)
    %% ======================================================================================
    subgraph Simulation_Newton["Simulation Domain - Newton"]
        SIM["newton_bridge_sim.py"]
        PIPE["simulation_pipeline.py"]
        S_LOGIC["bridge_sim_logic.py"]
        S_STATE["sim_state_manager.py"]
        S_PHYS["sim_physics_rules.py"]
        B_BUILD["bridge_builder.py"]
        B_VIS["bridge_visualizer.py"]
        B_ANA["bridge_analytics.py"]
    end
    
    subgraph AI_NeMo["AI Optimization Domain - NeMo"]
        OPT["nemo_global_optimizer.py"]
        OPT_L["nemo_optimizer_logic.py"]
        OPT_H["nemo_result_handler.py"]
        N_MODEL["nemo_model.py"]
        N_PRE["nemo_preprocessing.py"]
        T_GEN_ADV["truss_generator.py"]
        N_TRAIN["nemo_surrogate_trainer.py"]
        N_INF["nemo_inference.py"]
    end
    
    subgraph JAX_Solver["High-Speed Solver Domain - JAX"]
        J_SOLVE["jax_solver.py"]
        J_ASS["jax_truss_assembler.py"]
        J_FAIL["jax_truss_failure.py"]
    end
    
    subgraph Data_Generation["Dataset Generation Domain"]
        D_GEN["parametric_dataset_gen.py"]
        S_SOLVE["bridge_solver_headless.py"]
        S_BUILD["headless_newton_builder.py"]
        S_RUN["headless_sim_runner.py"]
    end
    
    subgraph Core_Rules_Geometry["Core Rules & Geometry"]
        RULES["rules.py"]
        R_BASE["bridge_rules_base.py"]
        R_CONST["rules_constants.py"]
        R_CHECK["rules_geometry_checks.py"]
        GEO["generate_geometry.py"]
        M_UTIL["mesh_utilities.py"]
        T_GEO["truss_geometry.py"]
    end
    
    subgraph Fabrication["Fabrication Domain"]
        F_MGR["fabrication_manager.py"]
        F_CUT["fabrication_cutlist.py"]
        F_DRAW["fabrication_drawing.py"]
        USD_EXP["export_usd_pxr.py"]
        USD_UTIL["usd_utils.py"]
        USD_GEO["bridge_usd_geometry.py"]
    end
    
    subgraph Solvers["Advanced Solvers"]
        AMGX["amgx_truss_engine.py"]
        NP_SLV["numpy_truss_solver.py"]
    end

    %% ======================================================================================
    %% 3. FUTURE HORIZONS (The Roadmap)
    %% ======================================================================================
    subgraph Future_Horizons["🚀 Future Horizons (Type 6 Expansion)"]
        direction TB
        Federation["🌐 Inter-Ark Federation (NetBird Mesh)"]
        Hardware["🔌 Hardware Bridge (Solar/Water/Power)"]
        Global_Trade["🚢 Global Trade Network"]
        AI_God["🧠 Maternal AI (Full Autonomy)"]
        
        Federation -.-> Ledger
        Hardware -.-> Fiat
        Global_Trade -.-> MerchAPI
        AI_God -.-> Steward
    end

    %% ======================================================================================
    %% CONNECTIVITY (Map-to-Territory)
    %% ======================================================================================

    %% Ark Internal
    UI_Quests --> Steward
    Steward --> Ledger
    Ledger --> Treasury
    Gov --> Justice
    UI_Justice --> ModAPI
    ModAPI --> Gov
    Gov --> Log
    UI_Merch --> MerchAPI
    MerchAPI --> Ledger
    MerchAPI --> Fiat
    Steward <--> Evol
    Treasury --> Party
    BB_Portal --> Treasury
    BB_Mobile --> Ledger
    BB_Display --> BB_Mobile
    BB_Portal --> BB_Analytics
    BB_Analytics --> BB_Portal

    %% Ark -> Engineering Bridge
    UI_Studio --> GEO
    UI_Studio --> D_GEN
    F_CUT --> Ledger
    USD_EXP --> UI_Dash

    %% Engineering Internal
    PIPE --> SIM
    SIM --> S_LOGIC & S_STATE & S_PHYS & B_BUILD & B_VIS & B_ANA
    S_LOGIC --> S_STATE & S_PHYS
    OPT --> OPT_L & OPT_H
    N_TRAIN --> N_MODEL & N_PRE
    N_INF --> N_MODEL & N_PRE
    J_SOLVE --> J_ASS & J_FAIL
    S_SOLVE --> S_BUILD & S_RUN & J_SOLVE
    RULES --> R_BASE
    R_BASE --> R_CONST & R_CHECK
    R_CHECK --> R_CONST
    GEO --> M_UTIL
    F_MGR --> F_CUT & F_DRAW
    F_CUT --> T_GEO
    F_DRAW --> T_GEO
    USD_EXP --> USD_UTIL & USD_GEO
    USD_GEO --> T_GEO
    NP_SLV --> AMGX
    B_ANA --> NP_SLV
    OPT_L --> N_MODEL & N_PRE & T_GEN_ADV
    D_GEN --> S_SOLVE
    D_GEN -.-> DATASET["physics_dataset_nemo.json"]
    DATASET -.-> N_TRAIN
    N_TRAIN -.-> MODEL_WEIGHTS["nemo_surrogate.pt"]
    MODEL_WEIGHTS -.-> OPT
    OPT_H -.-> CHAMPION["new_champion.json"]
    CHAMPION -.-> SIM
    SIM -.-> RESULTS["fea_results.json"]

    %% ======================================================================================
    %% STYLING (Dark Mode)
    %% ======================================================================================
    
    %% Ark Styling
    classDef ark fill:#3B82F6,stroke:#fff,color:#fff,stroke-width:2px
    class UI_Dash,UI_Quests,UI_Wallet,UI_Studio,UI_Justice,UI_Merch ark
    class Ledger,Gov,Identity,Config,Steward,Evol,Treasury,Fiat,MerchAPI,Party,ModAPI,Justice,Log ark

    %% Board Bored Styling (Purple)
    classDef boardbored fill:#8B5CF6,stroke:#fff,color:#fff,stroke-width:2px
    class BB_Portal,BB_Mobile,BB_Display,BB_Analytics boardbored

    %% Future Styling (Dotted/Ghost)
    classDef future fill:none,stroke:#fff,stroke-width:2px,stroke-dasharray: 5 5,color:#aaa
    class Federation,Hardware,Global_Trade,AI_God future

    %% Engineering Styling (Matches Input)
    classDef default fill:#2d2d2d,stroke:#fff,color:#fff
    classDef running fill:#ffcc00,stroke:#fff,stroke-width:4px,color:#000
    classDef success fill:#00cc66,stroke:#fff,color:#fff
    classDef failed fill:#ff3333,stroke:#fff,color:#fff
    
    class SIM,PIPE,S_LOGIC,S_STATE,S_PHYS,B_BUILD,B_VIS,B_ANA default
    class OPT,OPT_L,OPT_H,N_MODEL,N_PRE,T_GEN_ADV,N_TRAIN,N_INF default
    class J_SOLVE,J_ASS,J_FAIL,D_GEN,S_SOLVE,S_BUILD,S_RUN default
    class RULES,R_BASE,R_CONST,R_CHECK,GEO,M_UTIL,T_GEO default
    class F_MGR,F_CUT,F_DRAW,USD_EXP,USD_UTIL,USD_GEO default
    class AMGX,NP_SLV,CHAMPION,DATASET,RESULTS,MODEL_WEIGHTS default
