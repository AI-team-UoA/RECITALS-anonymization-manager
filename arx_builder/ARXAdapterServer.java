import org.deidentifier.arx.Data;
import py4j.GatewayServer;

public class ARXAdapterServer {
    /* This holds the data */
    private Data data;
    
    /* Loads the dataset from the given path. */   
    public static void load_dataset(String path) {
        
    }

    /* Starts the ARX adapter server. */
    public static void main(String[] args) {
        ARXAdapterServer server = new ARXAdapterServer();
        GatewayServer gatewayServer = new GatewayServer(server);
        gatewayServer.start();
        System.out.println("gh Hello World");
    }

    /* Grabs the quasi-identifiers */
    /* Pings the server. */
    public void ping() {
        System.out.println("Ping received");
    }
}