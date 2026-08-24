/// <summary>
/// NexusIds — Auto-generated constants matching shared_config/ids.yaml.
/// This is the SINGLE place in Unity that defines junction, strategy, vehicle,
/// and incident identifiers. All other scripts reference these constants.
/// DO NOT hardcode "J1", "green_extend", etc. anywhere else.
/// </summary>
namespace NexusTwin.Data
{
    public static class NexusIds
    {
        // Junction identifiers — must match backend TrafficState junction_id values
        public static class Junctions
        {
            public const string J1 = "J1";
            public const string J2 = "J2";
            public const string J3 = "J3";
            public static readonly string[] All = { J1, J2, J3 };
        }

        // Strategy type strings — must match backend strategy_type enum values
        public static class Strategies
        {
            public const string GreenExtend = "green_extend";
            public const string Diversion = "diversion";
            public const string DynamicLane = "dynamic_lane";
            public const string EmergencyPriority = "emergency_priority";
            public const string DoNothing = "do_nothing";
        }

        // Vehicle type strings — must match backend vehicle type values
        public static class Vehicles
        {
            public const string Car = "car";
            public const string Bus = "bus";
            public const string Truck = "truck";
            public const string Motorcycle = "motorcycle";
            public const string Ambulance = "ambulance";
            public const string Police = "police";
            public const string Fire = "fire";
        }

        // Incident type strings — must match backend incident type values
        public static class Incidents
        {
            public const string Accident = "accident";
            public const string Closure = "closure";
            public const string Surge = "surge";
            public const string Weather = "weather";
            public const string Emergency = "emergency";
        }
    }
}
