package mtdb;

import java.io.File;
import java.io.FileInputStream;
import java.io.InputStream;
import java.io.IOException;

import org.yaml.snakeyaml.Yaml;

public class Conf
{
	public static void testLoadFromStream() throws IOException {
		InputStream input = new FileInputStream(new File("conf/loadgen.yaml"));
		Yaml yaml = new Yaml();
		Object data = yaml.load(input);
		input.close();
		System.out.println(yaml.dump(data));
	}
}
