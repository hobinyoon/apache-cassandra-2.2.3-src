package mtdb;

public class LoadGen
{
	public static void main(String[] args)
	{
		try {
			Conf.testLoadFromStream();
		} catch (Exception e) {
			System.out.println("Exception: " + e);
		}
	}
}
