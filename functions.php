<?php
/**
 * Twenty Twenty-Two functions and definitions
 *
 * @link https://developer.wordpress.org/themes/basics/theme-functions/
 *
 * @package WordPress
 * @subpackage Twenty_Twenty_Two
 * @since Twenty Twenty-Two 1.0
 */

if ( ! function_exists( 'twentytwentytwo_support' ) ) :

	/**
	 * Sets up theme defaults and registers support for various WordPress features.
	 *
	 * @since Twenty Twenty-Two 1.0
	 *
	 * @return void
	 */
	function twentytwentytwo_support() {

		// Add support for block styles.
		add_theme_support( 'wp-block-styles' );

		// Enqueue editor styles.
		add_editor_style( 'style.css' );
	}

endif;

add_action( 'after_setup_theme', 'twentytwentytwo_support' );

if ( ! function_exists( 'twentytwentytwo_styles' ) ) :

	/**
	 * Enqueue styles.
	 *
	 * @since Twenty Twenty-Two 1.0
	 *
	 * @return void
	 */
	function twentytwentytwo_styles() {
		// Register theme stylesheet.
		$theme_version = wp_get_theme()->get( 'Version' );

		$version_string = is_string( $theme_version ) ? $theme_version : false;
		wp_register_style(
			'twentytwentytwo-style',
			get_template_directory_uri() . '/style.css',
			array(),
			$version_string
		);

		// Enqueue theme stylesheet.
		wp_enqueue_style( 'twentytwentytwo-style' );
	}

endif;

add_action( 'wp_enqueue_scripts', 'twentytwentytwo_styles' );

// Add block patterns
require get_template_directory() . '/inc/block-patterns.php';

/* 今日の日付を呼び出すショートコード */
function shortcode_today() {
    return date_i18n("Y年n月j日(D) G:i s");
}
add_shortcode('today_date', 'shortcode_today');

function console_log($data){
	echo '<script>';
	echo 'console.log('.json_encode($data).')';
	echo '</script>';
}

/* データベースに接続 */
function connect_DB() {
try {
  // 慣習としてPDOインスタンスはdbh(データベースハンドルの略)にする
	$db = new PDO("mysql:dbname=tomsky_wp1;host=localhost;charset=utf8", "tomsky_wp1","Magnez0ne765pro");
	$sql = "select distinct post_title from wp_posts";
	$result = $db->query($sql);
	foreach($result as $val){
		echo $val["post_title"],"<br/>";
	}
} catch(PDOException $e) {
  	echo "エラーメッセージ : " . $e -> getMessage();
}
}
add_shortcode('DB', 'connect_DB');


