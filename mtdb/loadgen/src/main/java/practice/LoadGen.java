package mtdb;

import java.io.ByteArrayInputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.InputStream;
import java.io.IOException;
import java.lang.String;
import java.util.List;

import org.yaml.snakeyaml.Yaml;

public class LoadGen
{
	public static void testLoadFromStream() throws IOException {
		InputStream input = new FileInputStream(new File("conf/loadgen.yaml"));
		Yaml yaml = new Yaml();
		Object data = yaml.load(input);
		input.close();
		System.out.println(yaml.dump(data));
	}

	public static void main(String[] args)
	{
		try {
			testLoadFromStream();
		} catch (Exception e) {
			System.out.println("Exception: " + e);
		}
	}
}
