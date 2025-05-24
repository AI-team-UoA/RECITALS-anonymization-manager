/* Dependencies. */
import org.deidentifier.arx.Data;
import org.deidentifier.arx.DataHandle;
import org.deidentifier.arx.AttributeType.Hierarchy.DefaultHierarchy;
import org.deidentifier.arx.Data.DefaultData;
import org.deidentifier.arx.ARXAnonymizer;
import org.deidentifier.arx.ARXConfiguration;
import org.deidentifier.arx.AttributeType;
import org.deidentifier.arx.criteria.DistinctLDiversity;
import org.deidentifier.arx.criteria.KAnonymity;
import org.deidentifier.arx.ARXResult;
import java.io.IOException;

/* This is a simple example where we run k anonymity on a set created inside the program. */
public class example {
    public static void main(String[] args) {
        DefaultData d = Data.create();

        /* Adds the names of the fields. */
        d.add("Name", "Last Name", "Age", "Country", "Disease");

        /* Creates random data and adds it to the table. */
        for (int i = 0; i < 100; i++) {
            d.add(tools.getRandName(), tools.getRandLastName(), tools.getRandAge(), tools.getRandCountry(), tools.getRandDisease());
        }

        /* Prints the records. */
        printData(d.getHandle());

        /* Treats everything as a except for the disease. */
        d.getDefinition().setAttributeType("Name", AttributeType.QUASI_IDENTIFYING_ATTRIBUTE);
        d.getDefinition().setAttributeType("Last Name", AttributeType.QUASI_IDENTIFYING_ATTRIBUTE);
        d.getDefinition().setAttributeType("Age", AttributeType.QUASI_IDENTIFYING_ATTRIBUTE);
        d.getDefinition().setAttributeType("Country", AttributeType.QUASI_IDENTIFYING_ATTRIBUTE);
        d.getDefinition().setAttributeType("Disease", AttributeType.INSENSITIVE_ATTRIBUTE);

        /* Creates the hierarchies. */
        createHierachies(d);

        /* Creates the anonymizer and uses the appropriate privacy model. */
        ARXAnonymizer a = new ARXAnonymizer();
        ARXConfiguration conf = ARXConfiguration.create();

        /* Uses either 2anonymity or 2diversity. */
        if (args[0].equals("kanonymity")) {
            conf.addPrivacyModel(new KAnonymity(2));
        } else if (args[0].equals("ldiversity")) {
            d.getDefinition().setAttributeType("Disease", AttributeType.SENSITIVE_ATTRIBUTE);
            conf.addPrivacyModel(new DistinctLDiversity("Disease", 2));
        }

        /* Runs the anonymization tool. */
        try {
            /* Anonymizes the data and prints it. */
            ARXResult anon_d = a.anonymize(d, conf);
            printData(anon_d.getOutput());
        } catch (IOException e){
            System.err.println(e.getMessage());
        }
    }

    /* Prints the data. */
    public static void printData(DataHandle dh) {
        System.out.printf(
            "%-30s %-30s %-30s %-30s %-30s\n",
            "Name",
            "Last Name",
            "Age",
            "Country",
            "Disease\n"
        );
        for (int i = 0; i < dh.getNumRows(); i++) {  
            System.out.printf(
                    "%-30s %-30s %-30s %-30s %-30s\n",
                    dh.getValue(i, 0),
                    dh.getValue(i, 1),
                    dh.getValue(i, 2),
                    dh.getValue(i, 3),
                    dh.getValue(i, 4)
                );
        }
        System.out.println();
        System.out.println();
    }

    /* Creates the hierarchies. */
    public static void createHierachies(Data d) {
        /* Creates the name hierarchy. */
        DefaultHierarchy nameH = new DefaultHierarchy();
        for (String name : d.getHandle().getDistinctValues(0)) {
            nameH.add(name, "*");
        }
        d.getDefinition().setHierarchy("Name", nameH);

        /* Creates the last name hierarchy. */
        DefaultHierarchy lastNameH = new DefaultHierarchy();
        for (String last_name : d.getHandle().getDistinctValues(1)) {
            lastNameH.add(last_name, "*");
        }
        d.getDefinition().setHierarchy("Last Name", lastNameH);

        /* Creates the age hierarchy. */
        DefaultHierarchy ageH = new DefaultHierarchy();
        for (int i = 0; i < 100; i++) {
            /* Age -> 5 year range -> 10 year range -> 20 year range -> 100 year range */
            String original = Integer.toString(i);
            int l1_start = (i/5)*5;
            int l2_start = (i/10)*10;
            int l3_start = (i/20)*20;
            String level1 = "["+l1_start+" - "+(l1_start+4)+"]";
            String level2 = "["+l2_start+" - "+(l2_start+9)+"]";
            String level3 = "["+l3_start+" - "+(l3_start+19)+"]";
            String level4 = "["+0+" - "+100+"]";
            ageH.add(original, level1, level2, level3, level4, "*");
        }
        d.getDefinition().setHierarchy("Age", ageH);

        /* Defines the country hierarchy. */
        DefaultHierarchy countryH = new DefaultHierarchy();
        for (String country : d.getHandle().getDistinctValues(3)) {
            /* Greece, Bulgaria, Albania -> Balkans -> * */
            if (country.equals("Greece") || country.equals("Bulgaria") || country.equals("Albania")) {
                countryH.add(country, "Balkans", "Europe");
            /* Spain, France -> Western Europe -> * */
            } else if (country.equals("Spain") || country.equals("France")) {
                countryH.add(country, "Western Europe", "Europe");
            /* Finland, Norway -> Nothern Europe -> * */
            } else if (country.equals("Finland") || country.equals("Norway")) {
                countryH.add(country, "Northern Europe", "Europe");
            }
        }
        d.getDefinition().setHierarchy("Country", countryH);
    }
}
