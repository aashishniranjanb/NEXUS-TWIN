namespace NexusTwin.Data
{
    /// <summary>Vehicle classification enum matching shared_config/ids.yaml.</summary>
    public enum VehicleType
    {
        Car,
        Bus,
        Truck,
        Motorcycle,
        Ambulance,
        Police,
        Fire
    }

    /// <summary>Strategy classification enum matching shared_config/ids.yaml.</summary>
    public enum StrategyType
    {
        GreenExtend,
        Diversion,
        DynamicLane,
        EmergencyPriority,
        DoNothing
    }

    /// <summary>Incident classification enum matching shared_config/ids.yaml.</summary>
    public enum IncidentType
    {
        Accident,
        Closure,
        Surge,
        Weather,
        Emergency
    }

    /// <summary>Camera mode enum per DESIGN_GUIDELINES.md §7-8.</summary>
    public enum CameraMode
    {
        Strategic,
        Free,
        IncidentFocus,
        EmergencyFollow
    }

    /// <summary>Game state machine states per GAME_STATE_MACHINE.md.</summary>
    public enum GameState
    {
        MainMenu,
        Cinematic,
        Briefing,
        Idle,
        Event,
        Analysis,
        Decision,
        Simulation,
        Comparison,
        Explanation,
        Approval,
        Apply,
        Result,
        Score,
        Failed,
        NextEvent
    }
}
