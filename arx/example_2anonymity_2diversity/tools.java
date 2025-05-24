/* Dependencies. */
import java.util.ArrayList;
import java.util.Arrays;
import java.util.LinkedHashMap;
import java.util.Random;

/* This is a helper class used for creating random entries. */
public class tools {
    public static String getRandAge() {
        Random r = new Random();
        return Integer.toString(r.nextInt(100));
    }

    public static String getRandName() {
        ArrayList<String> s = new ArrayList<>(Arrays.asList("John", "Elena", "Nick", "Anastasia", "Jimmys", "Victoria", "Natalia"));
        Random r = new Random();
        int pick = r.nextInt(s.size()-1);
        return s.get(pick);
    }

    public static String getRandLastName() {
        ArrayList<String> s = new ArrayList<>(Arrays.asList("Black", "White", "Paul", "Smith", "Garcia", "Rodriguez", "Miller"));
        Random r = new Random();
        int pick = r.nextInt(s.size()-1);
        return s.get(pick);
    }

    public static String getRandDisease() {
        ArrayList<String> s = new ArrayList<>(Arrays.asList("Heart-Disease", "Covid", "Influenza", "Diabetes", "Mental-Issue", "Kidney-Failure", "Fracture"));
        Random r = new Random();
        int pick = r.nextInt(s.size()-1);
        return s.get(pick);
    }

    public static String getRandCountry() {
        ArrayList<String> s = new ArrayList<>(Arrays.asList("Bulgaria", "Greece", "Albania", "Spain", "France", "Finland", "Norway"));
        Random r = new Random();
        int pick = r.nextInt(s.size()-1);
        return s.get(pick);
    }
}
